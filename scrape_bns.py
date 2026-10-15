"""
BNS (Bharatiya Nyaya Sanhita, 2023) Full Scraper
=================================================
Scrapes all 358 sections from https://devgan.in/all_sections_bns.php
and generates 3 dataset files:

1. bns_rag_dataset.json       — For RAG retrieval
2. bns_finetune_dataset.json  — For LLM fine-tuning (instruction format)
3. bns_scenarios_dataset.json — For reasoning / prediction training
"""

import json
import re
import time
import html
import os
import urllib.request
import urllib.error
import concurrent.futures
import nltk
from nltk.corpus import stopwords

# Download NLTK stopwords if not already present
nltk.download('stopwords', quiet=True)
ENGLISH_STOP_WORDS = set(stopwords.words('english'))

BASE_URL = "https://devgan.in"
LISTING_URL = f"{BASE_URL}/all_sections_bns.php"
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

# --- HTML Cleaning Utilities ---

def strip_html(raw_html):
    """Remove HTML tags and decode entities."""
    text = re.sub(r'<br\s*/?>', '\n', raw_html)
    text = re.sub(r'<li[^>]*>', '\n• ', text)
    text = re.sub(r'</li>', '', text)
    text = re.sub(r'<ol[^>]*>', '\n', text)
    text = re.sub(r'</ol>', '\n', text)
    text = re.sub(r'<strong>', '', text)
    text = re.sub(r'</strong>', '', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = html.unescape(text)
    # Clean up whitespace
    text = re.sub(r'\n\s*\n', '\n\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    return text.strip()


def fetch_page(url, retries=3):
    """Fetch a URL with retries and return decoded HTML string."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as resp:
                return resp.read().decode('utf-8', errors='replace')
        except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:
            print(f"  [RETRY {attempt+1}] Error fetching {url}: {e}")
            time.sleep(2)
    print(f"  [FAILED] Could not fetch {url} after {retries} retries")
    return None


# --- Phase 1: Extract section list from the listing page ---

def extract_section_list(listing_html):
    """Parse the listing page to get all section numbers and short titles."""
    # Pattern: <a href='/bns/section/N/' title='BNS Section N &raquo; Title..'>
    pattern = r"<a\s+href='(/bns/section/(\d+)/)'\s+title='BNS Section \d+\s+&raquo;\s+([^']+)'"
    matches = re.findall(pattern, listing_html)
    sections = []
    for path, num, title in matches:
        clean_title = html.unescape(title).rstrip('.')
        sections.append({
            'section': int(num),
            'title': clean_title,
            'url': f"{BASE_URL}{path}"
        })
    print(f"[INFO] Found {len(sections)} sections on listing page")
    return sections


# --- Phase 2: Scrape individual section pages ---

def extract_section_detail(section_html):
    """Extract chapter, description text from a section detail page."""
    chapter = ""
    chapter_match = re.search(r"<th class='title fill'>(Chapter\s+[^<]+)</th>", section_html)
    if chapter_match:
        chapter = html.unescape(chapter_match.group(1)).strip()

    # Extract description block
    desc_match = re.search(
        r"<tr class='mys-desc'>\s*<td colspan='2'>(.*?)</td>\s*</tr>",
        section_html, re.DOTALL
    )
    description = ""
    if desc_match:
        description = strip_html(desc_match.group(1))

    return chapter, description


def extract_punishment(description):
    """Try to extract punishment clause from the description."""
    punishment_patterns = [
        r'(?:shall be punished|punishable|punishment)[^.]*(?:imprisonment[^.]*|fine[^.]*|death[^.]*|community service[^.]*)\.',
        r'(?:shall be punished)[^.]+\.',
        r'(?:punished with)[^.]+\.',
    ]
    for pat in punishment_patterns:
        match = re.search(pat, description, re.IGNORECASE)
        if match:
            return match.group(0).strip()
    return ""


def generate_keywords(title, description):
    """Generate relevant keywords from title and description using NLTK stopwords."""
    # Use NLTK English stopwords + legal filler words
    stop_words = ENGLISH_STOP_WORDS | {
        'shall', 'may', 'upon', 'thereof', 'herein', 'wherein',
        'whoever', 'whatever', 'whichever', 'provided', 'section',
        'sub', 'clause', 'act', 'person', 'punishment', 'offence',
        'imprisonment', 'fine', 'years', 'months', 'term', 'extend',
        'punished', 'liable', 'guilty', 'commit', 'committed'
    }

    words = set()
    # Title words
    for w in re.findall(r'\b[a-zA-Z]{3,}\b', title.lower()):
        if w not in stop_words:
            words.add(w)

    # Important phrases from description (first 500 chars)
    desc_sample = description[:500].lower()
    for w in re.findall(r'\b[a-zA-Z]{4,}\b', desc_sample):
        if w not in stop_words and len(words) < 15:
            words.add(w)

    return sorted(list(words))[:12]


# --- Phase 3: Generate scenario dataset ---

SCENARIO_TEMPLATES = {
    # (section_numbers): list of scenario templates
    (63, 64, 65): [
        "A woman was sexually assaulted by a stranger while returning home from work at night.",
        "A man forced himself on a woman after threatening her with a knife.",
        "A minor girl was raped by her neighbor who lured her with candy.",
    ],
    (70,): [
        "A group of men abducted a woman and took turns sexually assaulting her.",
        "Three men gang-raped a woman after kidnapping her from a bus stop.",
    ],
    (74, 75): [
        "A man groped a woman on a crowded bus and made obscene remarks.",
        "A manager repeatedly made sexual comments to his female employee and demanded favors.",
        "A woman was molested by an unknown person at a public event.",
    ],
    (77,): [
        "A man installed a hidden camera in the women's changing room.",
        "Someone recorded a woman without her consent in the washroom using a phone camera.",
    ],
    (78,): [
        "A man kept following a woman to her house despite her asking him to stop.",
        "Someone has been repeatedly sending threatening messages and following a woman online and offline.",
    ],
    (80, 85, 86): [
        "A newly married woman was found dead under suspicious circumstances. Her in-laws demanded more dowry.",
        "A woman's husband and mother-in-law constantly harassed her for not bringing enough dowry, leading to her attempting suicide.",
    ],
    (100, 101, 103): [
        "A man was found dead in his apartment with stab wounds. His business partner is the prime suspect.",
        "During a heated argument, a person struck another with an iron rod, killing him instantly.",
        "A jealous ex-partner poisoned the victim by mixing pesticide in their food.",
    ],
    (105,): [
        "During a bar fight, a person pushed another who fell and hit his head, dying later in the hospital.",
        "A man hit another with a stick during a land dispute. The victim died three days later in the hospital.",
    ],
    (106,): [
        "A speeding car hit a pedestrian on the crosswalk, killing them instantly. The driver fled the scene.",
        "A bus driver was driving under the influence and ran over a cyclist, causing death.",
        "A truck driver fell asleep at the wheel and crashed into a family's car, killing two people.",
    ],
    (109,): [
        "A man fired a gunshot at his neighbor but missed. The bullet lodged in the wall.",
        "Someone tried to push a person off a building during a quarrel.",
    ],
    (111,): [
        "A criminal syndicate has been running an extortion racket targeting small business owners in the city.",
        "An organized gang has been carrying out contract killings and running illegal arms trade.",
    ],
    (113,): [
        "A group planted explosives in a crowded market area to create terror among citizens.",
        "Someone was caught planning to attack a government building with homemade bombs.",
    ],
    (114, 115, 116, 117): [
        "A man punched another person in the face during an argument, breaking his nose.",
        "Someone hit a person with a cricket bat during a dispute, fracturing their arm.",
        "A group of men beat up a shopkeeper causing multiple fractures and internal injuries.",
        "A person threw acid on another person's face during a road rage incident.",
    ],
    (118,): [
        "A person attacked another with a sharp knife causing deep cuts on the arms.",
        "Someone threw a glass bottle at a person in a bar, causing a deep wound on the head.",
    ],
    (124,): [
        "A jilted lover threw acid on a woman's face causing permanent disfigurement.",
        "Someone poured acid on a sleeping person as revenge.",
    ],
    (126, 127): [
        "A landlord locked a tenant inside the house and refused to let them leave until they paid rent.",
        "A group of people blocked a person's car and refused to let them pass on a public road.",
    ],
    (137, 138, 140): [
        "A child was kidnapped from outside their school by unknown persons in a van.",
        "A businessman was abducted by armed men who demanded a ransom of 50 lakhs.",
        "A minor girl was kidnapped from her village by traffickers.",
    ],
    (143, 144): [
        "A group was found trafficking young women from rural areas to urban centers for forced labor.",
        "Several children were rescued from a factory where they were forced to work without pay.",
    ],
    (152,): [
        "A person posted inflammatory content online that called for armed rebellion against the government.",
        "Someone distributed pamphlets encouraging secession and attacking national unity.",
    ],
    (196,): [
        "A person gave a provocative speech at a rally inciting violence between religious communities.",
        "Someone spread hateful messages on social media targeting a specific ethnic group, leading to riots.",
    ],
    (303, 304): [
        "My mobile phone was stolen from my pocket while I was travelling on the local train.",
        "Someone broke into my parked car and stole a laptop and cash worth Rs 50,000.",
        "A shoplifter was caught stealing clothes from a retail store.",
        "A pickpocket stole a wallet containing cash and debit cards from a crowded market.",
        "Someone snatched a gold chain from a woman walking on the road.",
    ],
    (305, 306): [
        "Burglars broke into my house at night while the family was sleeping and stole jewelry and cash.",
        "A person was robbed at knifepoint while withdrawing money from an ATM.",
    ],
    (307, 308, 309, 310): [
        "Three armed men barged into a jewelry shop, held the staff at gunpoint, and looted gold worth 2 crores.",
        "A group of robbers stopped a car on the highway, beat the driver, and robbed all valuables.",
        "Armed robbers attacked a bank van and looted Rs 1 crore at gunpoint.",
    ],
    (316, 317): [
        "A person's house was broken into while they were on vacation. Electronics and cash were stolen.",
        "Someone entered an office building after hours and stole computer equipment.",
    ],
    (318, 319): [
        "A person was cheated of Rs 5 lakhs through a fake investment scheme promising 50% returns.",
        "Someone created a fake website mimicking a bank and stole login credentials of thousands of users.",
        "A con artist impersonated a government official and collected bribes from people for fake services.",
        "An online seller took payment for a product but never delivered it and became unreachable.",
        "Someone used a cloned credit card to make unauthorized purchases worth Rs 2 lakhs.",
    ],
    (329, 330, 331): [
        "A contractor was paid Rs 10 lakhs in advance for construction work but misappropriated the funds.",
        "A company employee embezzled Rs 50 lakhs from the firm's accounts over two years.",
        "A trustee of a charitable organization diverted donated funds to personal accounts.",
    ],
    (336, 337, 338): [
        "Someone filed forged documents to claim ownership of a disputed property.",
        "A person forged a will to inherit property that belonged to their deceased relative.",
        "Someone created a fake degree certificate to get a government job.",
    ],
    (351, 352): [
        "A person deliberately set fire to a neighbor's house during a dispute.",
        "Someone committed arson by burning a rival's warehouse containing goods worth crores.",
    ],
    (356,): [
        "A man filed a false case of robbery to claim insurance money for items that were never stolen.",
        "A person made a defamatory speech about another at a public gathering, falsely accusing them of corruption.",
    ],
    (281,): [
        "A drunk driver was speeding through a residential area and nearly hit several pedestrians.",
        "A biker performing stunts on a public road crashed into a fruit vendor's cart.",
    ],
}


def generate_scenarios(sections_data):
    """Generate scenario-based dataset using templates + section descriptions."""
    scenarios = []

    # Template-based scenarios
    for section_nums, templates in SCENARIO_TEMPLATES.items():
        # Find matching section data
        matched = [s for s in sections_data if s['section'] in section_nums]
        if not matched:
            continue
        sections_str = ", ".join(
            f"Section {s['section']} ({s['title']})" for s in matched
        )
        punishment_parts = [s.get('punishment', '') for s in matched if s.get('punishment')]
        punishment_str = " | ".join(punishment_parts[:2]) if punishment_parts else "As prescribed under BNS, 2023."

        for template in templates:
            answer = (
                f"Based on the facts described, the applicable sections of the "
                f"Bharatiya Nyaya Sanhita (BNS), 2023 are: {sections_str}. "
                f"Punishment: {punishment_str} "
                f"This is a cognizable offense and an FIR should be registered under Section 173 BNSS, 2023."
            )
            scenarios.append({
                "scenario": template,
                "answer": answer,
                "sections": list(section_nums)
            })

    # Auto-generate additional scenarios from section titles for sections
    # not covered by templates
    covered = set()
    for nums in SCENARIO_TEMPLATES.keys():
        covered.update(nums)

    for s in sections_data:
        if s['section'] in covered:
            continue
        if not s.get('punishment'):
            continue
        # Only generate for sections with clear crime titles
        title_lower = s['title'].lower()
        skip_keywords = ['definition', 'explanation', 'general', 'application',
                         'commencement', 'repeal', 'saving', 'liability',
                         'abetment', 'attempt', 'punishment for']
        if any(kw in title_lower for kw in skip_keywords):
            continue

        scenario = f"A complaint has been filed regarding an incident involving: {s['title'].lower()}."
        answer = (
            f"The applicable section is Section {s['section']} ({s['title']}) of BNS, 2023. "
            f"Punishment: {s['punishment'] if s['punishment'] else 'As prescribed.'} "
            f"An FIR should be registered under Section 173 BNSS, 2023."
        )
        scenarios.append({
            "scenario": scenario,
            "answer": answer,
            "sections": [s['section']]
        })

    return scenarios


def generate_finetune_entries(sections_data):
    """Generate instruction-tuning dataset entries."""
    entries = []
    for s in sections_data:
        # Entry 1: Explain the section
        entries.append({
            "instruction": f"Explain Section {s['section']} of the Bharatiya Nyaya Sanhita (BNS), 2023.",
            "input": "",
            "output": (
                f"Section {s['section']} of BNS, 2023 deals with: {s['title']}.\n\n"
                f"Chapter: {s.get('chapter', 'N/A')}\n\n"
                f"Legal Provision:\n{s['text']}"
                + (f"\n\nPunishment: {s['punishment']}" if s.get('punishment') else "")
            )
        })

        # Entry 2: What is the punishment (if applicable)
        if s.get('punishment'):
            entries.append({
                "instruction": f"What is the punishment under Section {s['section']} of BNS, 2023?",
                "input": "",
                "output": (
                    f"Under Section {s['section']} ({s['title']}) of the Bharatiya Nyaya Sanhita, 2023, "
                    f"the punishment is: {s['punishment']}"
                )
            })

        # Entry 3: Which section covers this topic
        if s['title'] and len(s['title']) > 3:
            entries.append({
                "instruction": f"Which section of BNS, 2023 deals with {s['title'].lower()}?",
                "input": "",
                "output": (
                    f"Section {s['section']} of the Bharatiya Nyaya Sanhita (BNS), 2023 "
                    f"deals with {s['title']}. It falls under {s.get('chapter', 'the relevant chapter')} of the Act."
                )
            })

    return entries


# --- Main Execution ---

def main():
    print("=" * 60)
    print("BNS FULL SCRAPER — Bharatiya Nyaya Sanhita, 2023")
    print("=" * 60)

    # Step 1: Fetch listing page
    print("\n[STEP 1] Fetching section listing page...")
    listing_html = fetch_page(LISTING_URL)
    if not listing_html:
        print("[FATAL] Could not fetch listing page. Exiting.")
        return

    section_list = extract_section_list(listing_html)
    if not section_list:
        print("[FATAL] Could not extract section list. Exiting.")
        return

    # Step 2: Scrape each section detail page concurrently
    print(f"\n[STEP 2] Scraping {len(section_list)} individual section pages concurrently...")
    rag_dataset = [None] * len(section_list)
    total = len(section_list)

    def scrape_single_section(idx):
        sec = section_list[idx]
        num = sec['section']
        title = sec['title']
        url = sec['url']
        page_html = fetch_page(url)
        if not page_html:
            return idx, {
                "section": num,
                "title": title,
                "chapter": "",
                "text": "",
                "punishment": "",
                "keywords": generate_keywords(title, "")
            }
        chapter, description = extract_section_detail(page_html)
        punishment = extract_punishment(description)
        keywords = generate_keywords(title, description)
        return idx, {
            "section": num,
            "title": title,
            "chapter": chapter,
            "text": description,
            "punishment": punishment,
            "keywords": keywords
        }

    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
        futures = {executor.submit(scrape_single_section, idx): idx for idx in range(total)}
        completed = 0
        for future in concurrent.futures.as_completed(futures):
            idx, res = future.result()
            rag_dataset[idx] = res
            completed += 1
            if completed % 20 == 0 or completed == total:
                print(f"  Progress: Scraped {completed}/{total} sections...")

    # Step 3: Generate output files
    print(f"\n[STEP 3] Generating output dataset files...")

    # --- File 1: RAG Dataset ---
    rag_path = os.path.join(OUTPUT_DIR, "bns_rag_dataset.json")
    with open(rag_path, 'w', encoding='utf-8') as f:
        json.dump(rag_dataset, f, indent=2, ensure_ascii=False)
    print(f"  [OK] bns_rag_dataset.json - {len(rag_dataset)} sections")

    # Also copy to public/ for frontend
    public_dir = os.path.join(OUTPUT_DIR, "public")
    os.makedirs(public_dir, exist_ok=True)
    pub_path = os.path.join(public_dir, "bns_rag_dataset.json")
    with open(pub_path, 'w', encoding='utf-8') as f:
        json.dump(rag_dataset, f, indent=2, ensure_ascii=False)
    print(f"  [OK] public/bns_rag_dataset.json (copy for frontend)")

    # --- File 2: LLM Fine-tuning Dataset ---
    finetune_entries = generate_finetune_entries(rag_dataset)
    ft_path = os.path.join(OUTPUT_DIR, "bns_finetune_dataset.json")
    with open(ft_path, 'w', encoding='utf-8') as f:
        json.dump(finetune_entries, f, indent=2, ensure_ascii=False)
    print(f"  [OK] bns_finetune_dataset.json - {len(finetune_entries)} entries")

    # --- File 3: Scenarios Dataset ---
    scenarios = generate_scenarios(rag_dataset)
    sc_path = os.path.join(OUTPUT_DIR, "bns_scenarios_dataset.json")
    with open(sc_path, 'w', encoding='utf-8') as f:
        json.dump(scenarios, f, indent=2, ensure_ascii=False)
    print(f"  [OK] bns_scenarios_dataset.json - {len(scenarios)} scenarios")

    # Summary
    print("\n" + "=" * 60)
    print("SCRAPING COMPLETE")
    print("=" * 60)
    print(f"  Sections scraped:      {len(rag_dataset)}")
    print(f"  Fine-tune entries:     {len(finetune_entries)}")
    print(f"  Scenario entries:      {len(scenarios)}")
    print(f"  Output directory:      {OUTPUT_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
