"""Generate the Siddha365 static multi-page website from the content below."""

from html import escape
import hashlib
from pathlib import Path
import posixpath
import re
import shutil
from urllib.parse import unquote, urlsplit

# Optional image optimization using Pillow (PIL).
# Handled via dynamic import so missing PIL never triggers linter or module errors.
try:
    import importlib
    Image = importlib.import_module("PIL.Image")
    ImageOps = importlib.import_module("PIL.ImageOps")
except (ImportError, ModuleNotFoundError):
    Image = ImageOps = None


SITE = Path(__file__).resolve().parent
PHONE = "+91 78455 39622"
PHONE_TEL = "+917845539622"
WHATSAPP = "https://api.whatsapp.com/send/?phone=917845539622&text=Hello%20Siddha%20365%2C%20I%20would%20like%20to%20book%20an%20appointment.&type=phone_number&app_absent=0"
GOOGLE_SEARCH = "https://www.google.com/maps/search/?api=1&query=Siddha+365+Health+Care+Clinic+Villivakkam+Chennai"
GOOGLE_EMBED = "https://maps.google.com/maps?q=Siddha%20365%20Health%20Care%20Clinic%20Villivakkam%20Chennai&output=embed"
REVIEWS_API = "https://siddha365.com/wp-json/wp/v2/pages/7?_fields=content"
ASSET_VERSION = "20261005-compact-statistics-43"

LOGO = "assets/optimized/siddha365-header-lockup.webp"
FAVICON = "wp-content/uploads/2023/05/cropped-SASEE-siddha-logo-final-2-1-192x192.png"
DOCTOR = "wp-content/uploads/2026/02/Siddha-doctor-at-her-clinic.png"
HERO_ALT = "Dr. Sindhu V at Siddha365 Health Care Clinic"

CONDITIONS = [
    {
        "slug": "infertility", "title": "Infertility care", "category": "Women's health",
        "image": "wp-content/uploads/2023/05/Infertility-Treatment-1-1.png",
        "intro": "Fertility concerns can involve either partner, both partners, or have no clear cause at first. A careful assessment helps identify the right next step.",
        "why": "Pregnancy may take longer when ovulation is irregular, sperm count or movement is affected, the fallopian tubes are blocked, or conditions such as endometriosis or PCOS are present. Sometimes routine tests do not identify a cause. Fertility is a shared health concern, so assessment usually includes both partners.",
        "care": ["Arrange an assessment with a qualified fertility clinician; do not rely on symptoms alone to identify a cause.", "Testing and options depend on the findings. They can include treating an underlying condition, fertility medicines, surgery, or assisted conception such as IUI or IVF.", "Bring previous test reports and a list of medicines or supplements to the appointment. Ask about likely benefits, risks, costs, and alternatives before starting any treatment."],
        "safety": "Seek timely specialist advice if conception has been difficult. Do not delay evidence-based fertility evaluation while trying unproven remedies.",
        "sources": [("NHS: causes of infertility", "https://www.nhs.uk/conditions/infertility/causes/"), ("NHS: infertility treatment options", "https://www.nhs.uk/conditions/infertility/treatment/")],
    },
    {
        "slug": "pcod", "title": "PCOS / PCOD", "category": "Women's health",
        "image": "wp-content/uploads/2023/05/pcod-1-1.png",
        "intro": "PCOD is a commonly used name for polycystic ovary syndrome (PCOS), a hormone condition that can affect periods, skin, hair, fertility, and metabolic health.",
        "why": "The exact cause is not fully understood. Hormone signalling and insulin resistance may contribute, and the condition can run in families. Irregular periods, acne, extra facial hair, or difficulty conceiving can have other causes too, so these signs alone do not confirm PCOS.",
        "care": ["A clinician may assess symptoms and arrange hormone or metabolic blood tests; an ultrasound is used only when appropriate.", "Care is matched to the goal, such as cycle regulation, acne or hair symptoms, metabolic health, or fertility. A clinician may discuss lifestyle support and prescription medicines.", "If planning pregnancy, ask about fertility options. Avoid starting hormone medicines, supplements, or restrictive diets without individual advice."],
        "safety": "PCOS has no single cure, but symptoms can often be managed. Continue regular checks for associated health concerns with your clinician.",
        "sources": [("NHS: PCOS / PMOS overview and treatment", "https://www.nhs.uk/conditions/polyendocrine-metabolic-ovarian-syndrome-pmos/"), ("NIDDK: PCOS and diabetes research", "https://www.niddk.nih.gov/health-information/professionals/diabetes-discoveries-practice/links-pcos-diabetes")],
    },
    {
        "slug": "diabetes", "title": "Diabetes care", "category": "Metabolic health",
        "image": "wp-content/uploads/2023/05/diabetes1-1.png",
        "intro": "Diabetes has different types and causes. Blood tests and a clinician's assessment are needed to diagnose it and shape a safe care plan.",
        "why": "In type 2 diabetes, the body may not use insulin well or may not make enough of it, allowing blood glucose to rise. Genes, family history, age, activity, and other health factors can all play a part. Type 1 diabetes has a different cause and requires insulin treatment.",
        "care": ["Use prescribed diabetes medicines or insulin as directed. Do not stop or adjust them because symptoms improve or a traditional medicine is started.", "A care plan may include glucose monitoring, food and activity support, medicines, and regular checks of blood pressure, eyes, kidneys, nerves, and feet.", "Tell every clinician about all medicines, herbal products, supplements, and procedures you use so interactions and glucose changes can be considered."],
        "safety": "A new foot wound, worsening vision, repeated very high or low glucose readings, vomiting, confusion, or unusual drowsiness needs prompt medical advice.",
        "sources": [("NIDDK: Type 2 diabetes causes and management", "https://www.niddk.nih.gov/health-information/diabetes/overview/what-is-diabetes/type-2-diabetes"), ("NIDDK: diabetes medicines and treatments", "https://www.niddk.nih.gov/health-information/diabetes/overview/insulin-medicines-treatments")],
    },
    {
        "slug": "fire-cupping", "title": "Fire cupping", "category": "Traditional therapy",
        "image": "wp-content/uploads/2024/11/fire-cupping.png",
        "intro": "Fire cupping is a traditional dry-cupping method that uses heat to create suction in a cup placed on the skin.",
        "why": "People may seek cupping for muscle or body discomfort. Cupping does not diagnose the cause of pain, and research for many claimed uses is limited; any decision to use it should follow an assessment of the person's health and skin.",
        "care": ["Discuss the goal, expected limits, alternatives, and personal risks with a qualified clinician before a session.", "Use a trained practitioner, clean equipment, and careful heat handling. Do not apply cups to broken, inflamed, or infected skin.", "For persistent or severe pain, obtain a medical assessment instead of relying on cupping alone."],
        "safety": "Cupping can cause burns, bruising, persistent skin marks, scars, or infection. It may worsen some skin conditions and should not replace prescribed treatment.",
        "sources": [("NCCIH: cupping evidence and safety", "https://www.nccih.nih.gov/health/cupping")],
    },
    {
        "slug": "hijama-cupping", "title": "Hijama / cupping", "category": "Traditional therapy",
        "image": "wp-content/uploads/2024/11/vaccum-cupping.png",
        "intro": "Hijama usually refers to wet cupping, where the skin is pierced so a small amount of blood enters the cup. Dry cupping uses suction without piercing the skin.",
        "why": "People may seek cupping for pain or general wellbeing, but research is limited for many conditions and it is not a proven cure. Wet cupping adds risks because it breaks the skin and involves blood.",
        "care": ["Discuss the reason for treatment and safer alternatives with a qualified clinician first, especially if you have a bleeding condition, anaemia, diabetes, or take blood-thinning medicine.", "If wet cupping is considered, strict single-use sterile equipment and infection-control practices are essential.", "Continue prescribed care and follow up persistent symptoms with the appropriate medical specialist."],
        "safety": "Repeated wet cupping can cause blood loss or anaemia, and contaminated equipment can spread blood-borne infections. Cupping can also cause burns, scars, or infection.",
        "sources": [("NCCIH: cupping evidence and safety", "https://www.nccih.nih.gov/health/cupping")],
    },
    {
        "slug": "kati-vasthi", "title": "Kati Vasthi", "category": "Traditional therapy",
        "image": "wp-content/uploads/2024/11/massage.png",
        "intro": "Kati Vasthi is a traditional external therapy in which warm oil is retained over the lower back for a period of time.",
        "why": "It is offered as a supportive comfort practice for some people with lower-back discomfort. Back pain can also come from injuries, joint or disc conditions, nerve problems, infection, or other causes that need different care.",
        "care": ["Get persistent or recurring back pain assessed so the cause and appropriate care are understood first.", "If considering Kati Vasthi, discuss the expected benefit and risks with a qualified practitioner; test oil temperature carefully to prevent burns.", "Keep up any prescribed exercises, medicines, or follow-up plan. Treat this procedure as optional supportive care, not a replacement for diagnosis or proven treatment."],
        "safety": "Seek urgent care for back pain with new leg weakness, numbness around the groin, loss of bladder or bowel control, fever, or a recent serious injury.",
        "sources": [("Research paper: yoga with Kati Basti for chronic low-back pain", "https://pmc.ncbi.nlm.nih.gov/articles/PMC11388008/"), ("NHS: osteoarthritis care and support", "https://www.nhs.uk/conditions/osteoarthritis/treatment/")],
    },
    {
        "slug": "skin-problems", "title": "Skin problems", "category": "Skin health",
        "image": "wp-content/uploads/2023/05/skin-diseases-1.png",
        "intro": "Rashes, itching, acne, pigment changes, and infections are different problems with different causes. An accurate diagnosis comes before choosing a remedy.",
        "why": "Skin symptoms can be linked to irritation, allergy, infection, acne, eczema, psoriasis, medicines, or other health conditions. Similar-looking rashes can need very different treatments, and some skin changes need prompt examination.",
        "care": ["Arrange a clinician or dermatologist review for a persistent, painful, spreading, recurrent, or unexplained skin problem.", "Use gentle, fragrance-free skin care and avoid scratching or applying strong creams, acids, or unlabelled mixtures until the cause is understood.", "Follow the treatment plan for the diagnosed condition and ask before combining prescription creams with herbal products."],
        "safety": "Rapidly spreading redness, severe pain, fever, swelling around the eyes, or a rash with breathing difficulty needs urgent medical care.",
        "sources": [("American Academy of Dermatology: skin-care guidance", "https://www.aad.org/public/everyday-care/skin-care-basics/"), ("American Academy of Dermatology: acne diagnosis and treatment", "https://www.aad.org/public/diseases/acne/derm-treat/treat")],
    },
    {
        "slug": "hair-fall", "title": "Hair fall", "category": "Hair health",
        "image": "wp-content/uploads/2023/05/hair-fall-1.png",
        "intro": "Hair shedding can be temporary or ongoing. The best next step depends on the pattern and the underlying cause, rather than a one-size-fits-all oil or supplement.",
        "why": "Common contributors include inherited hair thinning, illness or major stress, hormonal or thyroid changes, nutritional deficiencies, scalp conditions, medicines, and tight hairstyles. Different causes call for different care.",
        "care": ["A clinician can examine the scalp and decide whether blood tests or a dermatology review are needed.", "Treat any identified cause and use gentle hair care; avoid tight styles, harsh chemical treatments, and unneeded high-dose supplements.", "Discuss treatment options and side effects before starting medicines. Early evaluation can help where hair loss is progressive."],
        "safety": "Sudden patchy loss, a painful or inflamed scalp, scarring, or hair loss with other new symptoms merits a timely medical review.",
        "sources": [("American Academy of Dermatology: causes of hair loss", "https://www.aad.org/public/diseases/hair-loss/causes/18-causes"), ("American Academy of Dermatology: hair-loss treatment", "https://www.aad.org/public/diseases/hair-loss/treatment/diagnosis-treat")],
    },
    {
        "slug": "corn-foot", "title": "Corn on the foot", "category": "Foot health",
        "image": "wp-content/uploads/2023/05/Corn-Foot-1.png",
        "intro": "A corn is a small area of thickened skin that usually forms where repeated pressure or friction affects the foot.",
        "why": "Tight or poorly fitting footwear, toe shape, and repeated rubbing can create pressure that thickens the skin. A corn can resemble a wart or another skin problem, so a painful or uncertain spot should be checked.",
        "care": ["Choose well-fitting shoes and consider soft padding to reduce pressure on the area.", "A clinician or pharmacist can advise whether gentle skin care or a treatment is suitable; avoid cutting or digging into the corn yourself.", "People with diabetes, poor circulation, reduced sensation, or a foot wound should get professional foot care rather than self-treating."],
        "safety": "See a clinician if it is very painful, inflamed, bleeding, infected, recurring, or if you have diabetes or circulation problems.",
        "sources": [("American Academy of Dermatology: treating corns and calluses", "https://www.aad.org/public/everyday-care/injured-skin/burns/treat-corns-calluses")],
    },
    {
        "slug": "piles", "title": "Piles (haemorrhoids)", "category": "Digestive health",
        "image": "wp-content/uploads/2023/05/IMG_20230501_210418-1-2048x1536.jpg",
        "image_alt": "A patient discussing a health concern with a Siddha clinician",
        "intro": "Piles are swollen blood vessels in or around the anus. Bleeding or pain should not automatically be assumed to be piles.",
        "why": "Constipation, straining to pass stool, pregnancy, heavy lifting, age, and excess weight can increase the chance of piles. A clinician can check whether another condition is causing rectal bleeding or discomfort.",
        "care": ["Fibre-rich foods, fluids, and avoiding straining can help keep stools soft; a pharmacist or clinician can advise on suitable symptom relief.", "If symptoms persist or recur, arrange a medical review. Some people need procedures or surgery after assessment.", "Follow advice about pain relief and any bleeding; do not use medicines that may be unsafe for your health conditions without checking first."],
        "safety": "Seek urgent medical attention for heavy or continuous bleeding, severe pain, fever, or pus. Rectal bleeding needs assessment, especially if it is new or recurrent.",
        "sources": [("NHS: piles causes and treatment", "https://www.nhs.uk/conditions/piles-haemorrhoids/")],
    },
    {
        "slug": "sinusitis", "title": "Sinusitis", "category": "Ear, nose & throat",
        "image": "wp-content/uploads/2023/05/IMG_20230501_210901-1-2048x1536.jpg",
        "image_alt": "A patient meeting with a clinician at the Siddha365 clinic",
        "intro": "Sinusitis is swelling of the lining of the sinuses, often after a cold or flu. Most short-term cases improve without antibiotics.",
        "why": "A viral infection commonly causes sinus swelling. Allergy and ongoing inflammation can contribute to recurring or longer-lasting symptoms. Swelling can block normal mucus drainage and cause pressure, congestion, or facial pain.",
        "care": ["Rest, fluids, avoiding smoke, and saline nose rinsing may help with mild symptoms; ask a pharmacist or clinician about suitable medicines.", "A clinician may consider a steroid nasal spray or allergy treatment. Antibiotics are only appropriate in selected cases after assessment.", "If symptoms recur, last a long time, or affect only one side, ask about further evaluation."],
        "safety": "Seek prompt care if you are very unwell, symptoms worsen, or you have a weakened immune system. Eye swelling or vision changes need urgent assessment.",
        "sources": [("NHS: sinusitis symptoms and treatment", "https://www.nhs.uk/conditions/sinusitis-sinus-infection/")],
    },
    {
        "slug": "wheezing", "title": "Wheezing and asthma", "category": "Breathing health",
        "image": "wp-content/uploads/2023/05/Wheezing-1.png",
        "intro": "Wheezing is a symptom, not a diagnosis. It can occur with asthma and with other breathing or respiratory conditions.",
        "why": "In asthma, sensitive airways become inflamed and narrow. Symptoms can be triggered by allergens, smoke, cold air, exercise, infections, or air pollution. Other causes of wheezing need their own assessment.",
        "care": ["Arrange a clinical assessment for repeated wheezing, cough, chest tightness, or breathlessness; breathing tests may be needed.", "Use prescribed inhalers exactly as directed and ask a clinician or pharmacist to check your inhaler technique.", "Keep an asthma action plan if you have asthma, attend reviews, and identify triggers with your care team."],
        "safety": "Severe or rapidly worsening difficulty breathing is an emergency. Follow your personal action plan and seek emergency care; do not wait for a traditional remedy to work.",
        "sources": [("NHS: asthma causes and treatment", "https://www.nhs.uk/conditions/asthma/")],
    },
    {
        "slug": "joint-pain", "title": "Joint pain", "category": "Joint health",
        "image": "wp-content/uploads/2023/05/join-pain-1.png",
        "intro": "Joint pain can have many causes, including injury, inflammation, infection, or osteoarthritis. Care depends on which joints are affected and why.",
        "why": "For osteoarthritis, protective joint cartilage gradually changes and the joint may become painful or stiff. Previous injury, age, family history, and other conditions can influence risk. Sudden hot or swollen joints may have a different cause.",
        "care": ["Get persistent, recurrent, or unexplained joint symptoms checked to confirm the cause.", "For osteoarthritis, regular movement and strength-building exercise are common parts of care; a clinician can suggest pain relief or supportive therapies.", "Avoid prolonged self-treatment and check before using pain medicines, especially if you have other health conditions or take other medication."],
        "safety": "A suddenly hot, very swollen joint, pain after a major injury, fever, or inability to bear weight needs prompt assessment.",
        "sources": [("NHS: osteoarthritis causes and overview", "https://www.nhs.uk/conditions/osteoarthritis/"), ("NHS: osteoarthritis treatment and support", "https://www.nhs.uk/conditions/osteoarthritis/treatment/")],
    },
    {
        "slug": "weight-management", "title": "Weight management", "category": "Metabolic health",
        "image": "wp-content/uploads/2023/05/weight-loss-1.png",
        "intro": "Weight is influenced by health, biology, medicines, sleep, stress, food access, and daily routines. A safe plan should be realistic and individual.",
        "why": "Weight change is not simply a matter of willpower. Health conditions, some medicines, hormones, environment, and life circumstances can make weight harder to manage. A clinician can check for contributing factors and discuss health goals without stigma.",
        "care": ["Choose sustainable food, movement, sleep, and behaviour changes that fit your health and circumstances.", "Ask a clinician about a structured support programme or medical options if appropriate; medicines are used alongside lifestyle support and require supervision.", "Avoid crash diets, unregulated weight-loss products, or stopping prescribed treatment to lose weight."],
        "safety": "Unexplained rapid weight change, disordered eating, or weight concerns alongside other new symptoms should be discussed with a healthcare professional.",
        "sources": [("NHS: overweight and obesity in adults", "https://www.nhs.uk/conditions/overweight-and-obesity/")],
    },
    {
        "slug": "autism", "title": "Autism support", "category": "Developmental support",
        "image": "wp-content/uploads/2023/05/autism-1.png",
        "intro": "Autism is a lifelong neurodevelopmental difference. Support should respect the person's strengths, communication, needs, and preferences.",
        "why": "There is no single known cause. Research points to multiple genetic and developmental factors; autism is not caused by poor parenting. It is identified through developmental history and a professional assessment, not a single blood test.",
        "care": ["Seek a developmental assessment if there are concerns about communication, interaction, sensory needs, or patterns of behaviour.", "Support may include speech and language, occupational, educational, developmental, or mental-health services tailored to the person.", "Discuss complementary products or therapies with the person's clinician, particularly for children. Do not use treatments that promise to cure autism or replace communication and developmental support."],
        "safety": "There is no medicine that treats autism itself. Medicines may be considered by a clinician for specific co-occurring conditions or symptoms.",
        "sources": [("CDC: autism causes and overview", "https://www.cdc.gov/autism/about/"), ("CDC: autism treatment and intervention", "https://www.cdc.gov/autism/treatment/index.html")],
    },
]

NAV = [
    ("Home", ""), ("About", "about"), ("Treatments", "treatments"),
    ("Gallery", "gallery"), ("Products", "products"), ("Reviews", "reviews"),
    ("Contact us", "contact-us"),
]

HOME_SLIDES = [
    ("wp-content/uploads/2024/11/FIRE-CUPPING-THERAPY-scaled.jpg", "Fire cupping therapy"),
    ("wp-content/uploads/2024/11/CUPPING-THERAPY-scaled.jpg", "Cupping therapy"),
    ("wp-content/uploads/2024/07/oilslider-11-scaled.jpg", "Traditional oil therapy"),
    ("wp-content/uploads/2024/04/new-slider-11-scaled.jpg", "Siddha clinic care"),
    ("wp-content/uploads/2024/04/new-slider-22-scaled.jpg", "Siddha medicines and care"),
    ("wp-content/uploads/2023/08/slider-3.png", "Care for families"),
    ("wp-content/uploads/2023/11/Understanding-Infertility-scaled.jpg", "Understanding infertility care"),
    ("wp-content/uploads/2024/04/slider-22-scaled.jpg", "Traditional Siddha treatments"),
    ("wp-content/uploads/2024/04/slider-55-scaled.jpg", "Herbal medicine"),
    ("wp-content/uploads/2024/11/HERBAL-STEAM-BATH-scaled.jpg", "Herbal steam bath"),
    ("wp-content/uploads/2024/11/varma-therapy-scaled.jpg", "Varma therapy"),
]

SPECIALTY_CARE = [
    ("✳", "Women’s Health", "PCOS, menstrual disorders, and other women’s health concerns need individual assessment."),
    ("◎", "Pediatric Care", "Discuss infant and child concerns with a qualified clinician and the appropriate specialist."),
    ("◌", "Chronic & Lifestyle Disorders", "Care conversations for ongoing health concerns, coordinated with current medical care."),
    ("◇", "Skin, Hair & Joint Care", "Skin, hair, and joint symptoms can have different causes; assessment guides the next step."),
    ("✿", "Holistic Siddha Treatment", "Discuss traditional methods and herbal medicines, including possible risks and interactions."),
    ("↗", "Patient-Centric Care", "Time for questions, clear options, and follow-up shaped around the person."),
]

VIDEOS = [
    ("b0nNtDSkhNA", "Fallopian tube health (Tamil)"),
    ("QETwB8eYBiU", "Clinic care and guidance"),
    ("XSo-HgTDsxo", "Siddha health and wellbeing"),
]

POPULAR_VIDEOS = [
    ("_-xuYNChZdU", "Children's fever care (Tamil)"),
    ("pv_BJ7naWDg", "Infertility treatment explained (Tamil)"),
    ("rzf1O5J7-KQ", "White discharge explained (Tamil)"),
    ("uEqrJIyOGTQ", "Obesity and weight-loss tips (Tamil)"),
    ("WlTU2yOrkaQ", "Hair-loss treatment tips (Tamil)"),
    ("PSJI4MYSD1k", "PCOD and menstrual health (Tamil)"),
    ("xomhOg3WH3s", "Headache care tips (Tamil)"),
    ("RyuwWtcDdn0", "Fat-loss guidance (Tamil)"),
]

YOUTUBE_CHANNEL = "https://www.youtube.com/@siddha365healthcare/videos"

PARTNER_LOGOS = [
    ("wp-content/uploads/2023/07/imcops1-320x285.jpg", "IMPCOPS"),
    ("wp-content/uploads/2023/07/skm1-320x285.jpg", "SKM Siddha"),
    ("wp-content/uploads/2023/07/nagaarjuna1-320x285.jpg", "Nagarjuna Herbal Concentrates"),
    ("wp-content/uploads/2023/07/tampol1-320x285.jpg", "Tampcol"),
    ("wp-content/uploads/2023/07/Dabur-1-320x285.png", "Dabur"),
    ("wp-content/uploads/2023/07/dr-siva1-320x285.jpg", "Dr Siva"),
    ("wp-content/uploads/2023/07/Himalaya1-320x285.png", "Himalaya"),
    ("wp-content/uploads/2023/07/vasu1-320x285.jpg", "Vasu"),
]


def esc(value):
    return escape(str(value), quote=True)


def rel(current, target):
    """Relative URL from a route directory to another route or site asset."""
    current_dir = current or "."
    value = posixpath.relpath(target or ".", current_dir)
    return "./" if value == "." else value.rstrip("/") + "/"


def asset(current, path):
    return posixpath.relpath(path, current or ".")


def page_shell(route, title, description, body, *, homepage=False, section=""):
    route_dir = route
    css = f"{asset(route_dir, 'assets/site.css')}?v={ASSET_VERSION}"
    refinements = f"{asset(route_dir, 'assets/refinement.css')}?v={ASSET_VERSION}"
    experience_css = f"{asset(route_dir, 'assets/experience.css')}?v={ASSET_VERSION}"
    experience_js = f"{asset(route_dir, 'assets/experience.js')}?v={ASSET_VERSION}"
    js = f"{asset(route_dir, 'assets/site.js')}?v={ASSET_VERSION}"
    boot = f"{asset(route_dir, 'assets/boot.js')}?v={ASSET_VERSION}"
    review_script = f'<script defer src="{asset(route_dir, "assets/reviews.js")}?v={ASSET_VERSION}"></script>' if 'data-live-reviews-url' in body else ''
    active_section = section or (route.split("/", 1)[0] if route else "")
    about_href = rel(route_dir, "about")
    about_active = (active_section == "about")
    about_active_attr = ' aria-current="page"' if about_active else ""
    nav_items = []
    for label, target in NAV:
        is_active = (target == active_section) or (target == "" and not active_section)
        href = rel(route_dir, target)
        item_class = ' class="nav-item-about"' if target == "about" else ""
        nav_items.append(f'<li{item_class}><a href="{href}"' + (' aria-current="page"' if is_active else "") + f'>{label}</a></li>')
    nav_html = "\n".join(nav_items)
    logo = asset(route_dir, LOGO)
    favicon = asset(route_dir, FAVICON)
    tel = f"tel:{PHONE_TEL}"
    dialog = ""
    if homepage:
        dialog = f'''<dialog class="visit-dialog" id="visit-dialog" aria-labelledby="dialog-title">
  <div class="dialog-content"><div class="dialog-top"><div><p class="eyebrow">Siddha365 · Chennai</p><h2 id="dialog-title">Plan a clinic visit</h2></div><button class="dialog-close" type="button" data-dialog-close aria-label="Close appointment message">×</button></div>
    <p>Speak with the clinic about an appointment, opening hours, or the right next step for your concern.</p>
    <div class="dialog-actions"><a class="button" href="{WHATSAPP}" target="_blank" rel="noopener noreferrer">Message on WhatsApp ↗</a><a class="button button-secondary" href="{tel}">Call {PHONE}</a></div>
  </div>
</dialog>'''
    html = f'''<!doctype html>
<html lang="en" class="no-js">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#0c110e">
  <meta name="description" content="{esc(description)}">
  <meta name="referrer" content="strict-origin-when-cross-origin">
  <meta http-equiv="Content-Security-Policy" content="default-src 'self'; base-uri 'self'; object-src 'none'; form-action 'self'; script-src 'self'; style-src 'self'; img-src 'self' https://i.ytimg.com; font-src 'self'; connect-src 'self' https://siddha365.com; frame-src https://www.youtube-nocookie.com https://maps.google.com https://www.google.com; upgrade-insecure-requests">
  <title>{esc(title)} | Siddha365 Health Care Clinic</title>
  <link rel="canonical" href="https://siddha365.com/{route + '/' if route else ''}">
  <link rel="icon" type="image/png" href="{favicon}">
  <link rel="preload" as="image" href="{logo}">
  <script src="{boot}"></script>
  <link rel="stylesheet" href="{css}">
  <link rel="stylesheet" href="{refinements}">
  <link rel="stylesheet" href="{experience_css}">
  <script defer src="{experience_js}"></script>
  <script defer src="{js}"></script>
  {review_script}
</head>
<body class="page-{section or ('home' if homepage else route.split('/')[0])}">
  <div class="page-loader" aria-hidden="true"><div class="loader-mark"><img src="{logo}" alt="" width="150" height="92"><span class="loader-scan"></span></div><span class="loader-label">Siddha365 · Care, with you in mind</span><span class="loader-line"></span></div>
  <a class="skip-link" href="#main-content">Skip to content</a>
  <div class="utility-bar"><div class="container utility-inner"><p>Traditional Siddha care · Chennai</p><div class="utility-actions"><p><a href="{tel}">Call {PHONE}</a><span class="utility-hours"><span aria-hidden="true"> &nbsp;·&nbsp; </span>Mon–Sat, 10:30 am–1:30 pm &amp; 7–9:30 pm</span></p><button class="motion-toggle" type="button" data-motion-toggle aria-pressed="false">Pause motion</button></div></div></div>
  <header class="site-header">
    <div class="nav-capsule">
      <a class="brand" href="{rel(route_dir, '')}" aria-label="Siddha365 home"><img src="{logo}" alt="Siddha 365 Health Care Clinic" width="138" height="84"></a>
      <nav class="nav-menu" aria-label="Main navigation"><ul class="nav-links" id="primary-navigation">{nav_html}<li class="nav-drawer-cta"><a class="button button-small nav-cta-drawer" href="{WHATSAPP}" target="_blank" rel="noopener noreferrer">Book appointment ↗</a></li></ul></nav>
      <div class="nav-actions">
        <a class="nav-pill-about" href="{about_href}"{about_active_attr}>About us</a>
        <a class="button button-small nav-cta" href="{WHATSAPP}" target="_blank" rel="noopener noreferrer"><span class="nav-cta-text-full">Book Appointment</span><span class="nav-cta-text-short">Book</span><span class="nav-cta-arrow" aria-hidden="true"> ↗</span></a>
        <button class="menu-toggle" type="button" aria-label="Open navigation" aria-expanded="false" aria-controls="primary-navigation"><span class="menu-icon" aria-hidden="true"></span></button>
      </div>
    </div>
  </header>
  {body}
  {footer(route_dir)}
  {dialog}
  <dialog class="media-dialog" id="video-dialog" aria-labelledby="video-dialog-title"><div class="media-dialog-head"><div><p class="eyebrow">Siddha365 · Watch &amp; learn</p><h2 id="video-dialog-title">Clinic video</h2></div><button class="dialog-close" type="button" data-dialog-close aria-label="Close video">×</button></div><div class="video-dialog-player" data-video-player></div></dialog>
  <dialog class="review-dialog" id="review-dialog" aria-labelledby="review-dialog-title"><div class="media-dialog-head"><h2 id="review-dialog-title">Patient review</h2><button class="dialog-close" type="button" data-dialog-close aria-label="Close review">×</button></div><div data-review-detail></div></dialog>
</body>
</html>'''
    return html


def footer(route):
    home = rel(route, "")
    treatment = rel(route, "treatments")
    about = rel(route, "about")
    reviews = rel(route, "reviews")
    contact = rel(route, "contact-us")
    gallery = rel(route, "gallery")
    products = rel(route, "products")
    tel = f"tel:{PHONE_TEL}"
    logo = asset(route, LOGO)
    partner_items = "".join(f'<div class="partner-logo"><img src="{asset(route, path)}" alt="{esc(name)}" loading="lazy" decoding="async"></div>' for path, name in PARTNER_LOGOS)
    return f'''<footer class="footer">
  <section class="container partner-section" aria-labelledby="partner-title">
    <div class="partner-heading"><h2 id="partner-title">Our herbal partners</h2></div>
    <div class="partner-marquee" aria-label="Siddha365 herbal partners"><div class="partner-track"><div class="partner-set">{partner_items}</div><div class="partner-set" aria-hidden="true">{partner_items}</div></div></div>
  </section>
  <div class="container footer-grid">
    <div class="footer-brand"><a class="brand" href="{home}" aria-label="Siddha365 home"><img src="{logo}" alt="Siddha 365 Health Care Clinic"></a><p>Thoughtful Siddha care with personal attention in Chennai. Every concern starts with a conversation and an individual assessment.</p></div>
    <div><h2 class="footer-title">Explore</h2><div class="footer-links"><a href="{treatment}">Treatments</a><a href="{about}">About the clinic</a><a href="{gallery}">Gallery</a><a href="{products}">Products</a><a href="{reviews}">Google reviews</a></div></div>
    <div><h2 class="footer-title">Visit</h2><div class="footer-links"><a href="{contact}">Clinic locations</a><a href="{contact}#hours">Opening hours</a><a href="{tel}">{PHONE}</a><a href="{WHATSAPP}" target="_blank" rel="noopener noreferrer">WhatsApp appointments</a></div></div>
    <div><h2 class="footer-title">Clinic hours</h2><div class="footer-links"><span>Monday – Saturday</span><span>10:30 am – 1:30 pm</span><span>7:00 pm – 9:30 pm</span><span>Sunday · by appointment</span></div></div>
  </div>
  <div class="footer-bottom container"><p>© 2026 Siddha365 Health Care Clinic</p><p>Health information on this site is general and does not replace an individual medical consultation.</p></div>
</footer>'''


def breadcrumb(route, title):
    crumbs = [f'<a href="{rel(route, "")}">Home</a>']
    if route.startswith("treatments"):
        crumbs.extend([f'<span class="separator" aria-hidden="true">/</span>', f'<a href="{rel(route, "treatments")}">Treatments</a>'])
    crumbs.extend([f'<span class="separator" aria-hidden="true">/</span>', f'<span aria-current="page">{esc(title)}</span>'])
    return '<nav class="breadcrumbs" aria-label="Breadcrumb">' + "".join(crumbs) + "</nav>"


def image_for(route, path, alt, cls="", *, loading=None, priority=False):
    cls_attr = f' class="{cls}"' if cls else ""
    loading = loading or ("eager" if "page-hero-art" in cls else "lazy")
    priority_attr = ' fetchpriority="high"' if priority or loading == "eager" else ""
    return f'<img{cls_attr} src="{asset(route, path)}" alt="{esc(alt)}" loading="{loading}" decoding="async"{priority_attr}>'


def condition_card(route, condition):
    href = rel(route, "treatments/" + condition["slug"])
    image = image_for(route, condition["image"], condition.get("image_alt", condition["title"]), "condition-image")
    return f'''<a class="condition-card reveal" href="{href}">
      {image}<div class="condition-body"><span class="tag">{esc(condition['category'])}</span><h3>{esc(condition['title'])}</h3><p>{esc(condition['intro'])}</p><span class="text-link">Read the care guide</span></div>
    </a>'''


def review_rows_html(route):
    # Only the live feed may populate review cards; no testimonials are stored here.
    rows = "".join(f'<div class="review-marquee" role="group" aria-label="Google reviews, row {i + 1}"><div class="review-marquee-track"><div class="review-group" data-review-group></div><div class="review-group" data-review-duplicate aria-hidden="true"></div></div></div>' for i in range(2))
    logo = asset(route, LOGO)
    return f'''<div class="review-feed-placeholder" data-review-placeholder><img src="{logo}" width="112" height="68" alt="Siddha365"><div><strong data-review-placeholder-title>Patient experiences, in their own words</strong><p data-review-placeholder-copy>Reviews will appear here when the clinic’s Google review feed connects.</p></div></div><div class="review-marquees" data-review-rows hidden>{rows}</div><noscript><p class="medical-note">Enable JavaScript to load current reviews from the clinic’s Google review feed.</p></noscript>'''


def nasagra_home_section():
    route = ""
    diagram = image_for(
        route,
        "wp-content/uploads/2026/02/thepranabody.png",
        "Traditional illustration used by the clinic to describe pranayama concepts; it is not an anatomical diagram",
        "nasagra-art-image",
    )
    return f'''<section class="section home-nasagra-section" id="nasagra-mudra"><div class="container"><div class="section-head"><div><p class="eyebrow">Traditional breathing practice · Learning guide</p><h2>Nasagra <span class="accent">Mudra</span></h2><p class="lead">A traditional hand position used in alternate-nostril breathing. This learning guide presents the practice as a cultural and wellness tradition, not as a treatment or cure for disease.</p></div></div><blockquote class="traditional-quote" lang="ta">“வளி, அழல், ஐயம் சமநிலையில் இருந்தால் ஆரோக்கியம்; அவை சீர்கெட்டால் நோய்.”</blockquote><div class="nasagra-page-grid"><div class="condition-content">
  <section class="prose-panel reveal"><h3>About the practice</h3><p>In descriptions of Nasagra Mudra, the thumb rests near one nostril while the ring and little fingers rest near the other. Some traditions use Vishnu Mudra, folding the index and middle fingers into the palm. The left hand may rest comfortably on the knee. Hand positions vary across teachers and traditions.</p></section>
  <section class="prose-panel reveal"><h3>How it is traditionally described</h3><ol class="nasagra-steps"><li>Sit in a comfortable position and keep the breath natural.</li><li>If a qualified instructor has shown you the technique, gently close one nostril and breathe through the other without straining.</li><li>Do not force, hold, or deliberately deepen the breath. Stop and rest if you feel dizzy, uncomfortable, or short of breath.</li></ol></section>
  <section class="prose-panel reveal"><h3>Benefits and evidence</h3><p>People may explore breathing practices for general wellbeing or as part of yoga. Research on yoga and breathing techniques varies, and this practice should not be presented as a cure for a medical condition or used in place of medical care.</p></section>
  <section class="prose-panel reveal"><h3>Safety and guidance</h3><p>Learn from a qualified instructor. If you have a health condition, are pregnant, are older, or have concerns about whether breath practice is suitable for you, discuss it with your healthcare provider first. Avoid forceful breathing and stop if you feel unwell.</p><div class="source-list"><a href="https://www.nccih.nih.gov/health/yoga-effectiveness-and-safety" target="_blank" rel="noopener noreferrer">NCCIH: Yoga effectiveness and safety ↗</a><a href="https://www.cuh.nhs.uk/patient-information/breathing-exercises/" target="_blank" rel="noopener noreferrer">Cambridge University Hospitals: Breathing exercises ↗</a></div></section>
  <p class="medical-note"><strong>Please note:</strong> This is general educational information, not a diagnosis or personal treatment plan. Do not delay medical assessment or stop a prescribed treatment to try a breathing practice.</p>
</div><figure class="nasagra-art reveal">{diagram}<figcaption>Traditional illustration provided in the clinic’s original website material. Its labels represent traditional concepts, not medical anatomy.</figcaption></figure></div></div></section>'''


def care_explorer():
    categories = [
        ("women", "Women’s Health Care", "Care through different stages of life", "Explore guides to fertility and menstrual health, and prepare for a conversation about your needs.", ["infertility", "pcod"]),
        ("skin", "Skin & Hair", "Start with understanding your concern", "Find information about skin, hair and foot concerns, with guidance on assessment and next steps.", ["skin-problems", "hair-fall", "corn-foot"]),
        ("movement", "Joints & Cupping Therapy", "Explore comfort, movement and care", "Read about joint concerns and traditional therapies, including what to discuss with your clinician.", ["joint-pain", "kati-vasthi", "fire-cupping", "hijama-cupping"]),
        ("family", "Family & Child Care", "Information for everyday health questions", "Browse care guides for ongoing concerns and learn when individual assessment or specialist care is needed.", ["diabetes", "weight-management", "sinusitis", "wheezing", "piles", "autism"]),
    ]
    by_slug = {item['slug']: item for item in CONDITIONS}
    tabs = []
    panels = []
    for index, (key, label, title, copy, slugs) in enumerate(categories):
        tabs.append(f'<button type="button" role="tab" id="care-tab-{key}" aria-controls="care-panel-{key}" aria-selected="{str(index == 0).lower()}" data-care-tab="{key}">{label}<span aria-hidden="true">↗</span></button>')
        featured = by_slug[slugs[0]]
        image = image_for('', featured['image'], featured['title'], 'care-explorer-image')
        links = ''.join(f'<a class="care-guide-link" href="treatments/{slug}/"><span class="guide-index" aria-hidden="true">0{i + 1}</span><span><strong>{esc(by_slug[slug]["title"])}</strong><small>Read the care guide</small></span><span class="guide-arrow" aria-hidden="true">↗</span></a>' for i, slug in enumerate(slugs))
        panels.append(f'<section class="care-panel" id="care-panel-{key}" role="tabpanel" aria-labelledby="care-tab-{key}" tabindex="0" data-care-panel="{key}"><div class="care-panel-overview"><div class="care-panel-photo">{image}<span class="care-photo-caption">Individual care. Clear next steps.</span></div><div class="care-panel-intro"><p class="eyebrow">{label}</p><h3>{title}</h3><p>{copy}</p><a class="text-link" href="contact-us/">Talk to the clinic</a></div></div><div class="care-guide-list">{links}</div></section>')
    return f'<div class="care-explorer" data-care-explorer><div class="care-tabs" role="tablist" aria-label="Explore care by category">{"".join(tabs)}</div><div class="care-panels">{"".join(panels)}</div><p class="care-explorer-note"><span aria-hidden="true">✦</span> Every person is different. An individual consultation helps determine the right next step.</p></div>'


def homepage():
    route = ""
    slides = "".join(
        f'<figure class="home-slide">{image_for(route, path, label, "home-slide-image", loading="eager" if index == 0 else "lazy", priority=index == 0)}</figure>'
        for index, (path, label) in enumerate(HOME_SLIDES)
    )
    explorer = care_explorer()
    stats = "".join([
        '<article class="home-stat"><span class="stat-icon" aria-hidden="true"><svg viewBox="0 0 48 48"><path d="M8 37V10M8 37h33M13 29l9-9 7 7 12-14M33 13h8v8"/></svg></span><strong data-count-to="5">5</strong><span class="stat-label">Year of experience</span></article>',
        '<article class="home-stat"><span class="stat-icon" aria-hidden="true"><svg viewBox="0 0 48 48"><g transform="rotate(-42 18 24)"><rect x="10" y="8" width="15" height="32" rx="7.5"/><path d="M10 24h15"/></g><g transform="rotate(42 32 24)"><rect x="25" y="12" width="13" height="27" rx="6.5"/><path d="M25 25.5h13"/></g></svg></span><strong data-count-to="500">500</strong><span class="stat-label">Health concerns supported</span></article>',
        '<article class="home-stat"><span class="stat-icon" aria-hidden="true"><svg viewBox="0 0 48 48"><circle cx="24" cy="24" r="17"/><path d="M24 12v24M18 18h9a5 5 0 0 1 0 10h-7a5 5 0 0 0 0 10h10M7 10h10M31 38h10"/></svg></span><strong data-count-to="700">700</strong><span class="stat-label">Treatments</span></article>',
        '<article class="home-stat"><span class="stat-icon" aria-hidden="true"><svg viewBox="0 0 48 48"><circle cx="24" cy="24" r="18"/><path d="M17 20h.1M31 20h.1M16 28c2.2 4.2 4.8 6 8 6s5.8-1.8 8-6"/></svg></span><strong data-count-to="5000">5,000</strong><span class="stat-label">Clients served</span></article>',
    ])
    video_cards = "".join(f'''<article class="video-card"><button class="video-poster" type="button" data-youtube-id="{esc(vid)}" data-youtube-title="{esc(label)}" aria-label="Play {esc(label)}"><img src="https://i.ytimg.com/vi/{esc(vid)}/hqdefault.jpg" alt="" loading="lazy" decoding="async"><span class="video-play-icon" aria-hidden="true">▶</span></button><p>{esc(label)}</p></article>''' for vid, label in VIDEOS)
    home_video_cards = "".join(f'''<article class="home-video-card"><button class="home-video-poster" type="button" data-youtube-id="{esc(vid)}" data-youtube-title="{esc(label)}" aria-label="Play {esc(label)}"><img src="https://i.ytimg.com/vi/{esc(vid)}/mqdefault.jpg" alt="" loading="lazy" decoding="async"><span class="video-play-icon" aria-hidden="true">▶</span></button><p>{esc(label)}</p></article>''' for vid, label in POPULAR_VIDEOS)
    review_cards = review_rows_html(route)
    nasagra_section = nasagra_home_section()
    body = f'''<main id="main-content">
  <section class="home-gallery-section"><div class="hero-glow" data-hero-glow aria-hidden="true"></div><div class="hero-orbit" aria-hidden="true"></div><div class="container"><div class="home-hero-stage"><div class="home-gallery" data-carousel><div class="carousel-controls home-gallery-controls"><button class="icon-button" type="button" data-carousel-prev aria-label="Previous clinic image">←</button><button class="icon-button" type="button" data-carousel-next aria-label="Next clinic image">→</button></div><div class="home-gallery-track" data-carousel-track data-autoplay="true" data-scroll-step="full" aria-label="Clinic treatments and care images">{slides}</div></div><div class="home-stage-shade" aria-hidden="true"></div><div class="home-hero-copy home-stage-copy"><p class="eyebrow">Traditional Siddha care · Chennai</p><h1>Thoughtful care, <span class="accent">rooted in tradition</span></h1><p>Meet Dr. Sindhu and explore personal care at Siddha365 Health Care Clinic.</p><div class="hero-actions home-hero-actions"><a class="button" href="{WHATSAPP}" target="_blank" rel="noopener noreferrer">Book an appointment ↗</a><a class="button button-secondary" href="#specialized-care">Explore your care</a></div><div class="home-hero-details"><span>Dr. Sindhu V. · BSMS, MD (Siddha)</span><a href="contact-us/">Two locations in Chennai <span aria-hidden="true">↗</span></a></div></div><aside class="home-video-rail home-stage-videos" aria-label="Videos from the Siddha365 YouTube channel"><div class="home-video-rail-head"><div><p class="eyebrow">Watch &amp; learn</p><h2>From our <span class="accent">channel</span></h2></div><a class="text-link" href="{YOUTUBE_CHANNEL}" target="_blank" rel="noopener noreferrer">YouTube</a></div><div class="home-video-rail-window" data-video-rail><div class="home-video-rail-track" data-video-rail-track>{home_video_cards}</div></div></aside></div></div></section>

  <section class="section home-intro"><div class="container home-intro-grid"><div class="home-intro-copy reveal"><p class="eyebrow">Siddha 365 Health Care</p><h2>Traditional care rooted in <span class="accent">Tamil Siddha</span></h2><p class="home-tamil" lang="ta">பாரம்பரிய சித்த மருத்துவத்தின் மூலம் முழுமையான இயற்கை சிகிச்சை.</p><p>Siddha365 Health Care Clinic is guided by Dr. Sindhu V., B.S.M.S., M.D. (Siddha). Rooted in Tamil Siddha tradition, the clinic offers individual consultations with careful assessment, a respectful conversation about each person’s needs, and clear next steps.</p><div class="hero-actions"><a class="button" href="{WHATSAPP}" target="_blank" rel="noopener noreferrer">Book an appointment ↗</a><a class="button button-secondary" href="about/">About the clinic</a></div></div><div class="home-intro-image reveal">{image_for(route, "wp-content/uploads/2026/02/new-doc.jpg", "Herbs prepared using traditional Siddha methods")}</div></div></section>

  <section class="section home-care-section" id="specialized-care"><div class="container"><div class="section-head reveal"><div><p class="eyebrow">Specialized care by Dr. Sindhu V</p><h2>Find care that <span class="accent">speaks to you.</span></h2><p>Choose an area to explore helpful guides and your next step.</p></div><a class="text-link" href="treatments/">All 15 care guides</a></div>{explorer}</div></section>

  <section class="home-stats-band" aria-label="Siddha365 clinic statistics">{image_for(route, "wp-content/uploads/2023/05/IMG_20230517_195232-1-2048x1536.jpg", "", "home-stats-background", loading="lazy")}<div class="container home-stats-grid">{stats}</div></section>

  <section class="section video-section"><div class="container carousel-shell" data-carousel><div class="section-head reveal"><div><p class="eyebrow">Watch &amp; learn</p><h2>From the Siddha365 <span class="accent">YouTube channel</span></h2><p>Scroll through clinic videos and health conversations. Select a video to play it here.</p></div><div class="carousel-controls"><button class="icon-button" type="button" data-carousel-prev aria-label="Scroll videos left">←</button><button class="icon-button" type="button" data-carousel-next aria-label="Scroll videos right">→</button><button class="icon-button" type="button" data-carousel-pause aria-pressed="false" aria-label="Pause automatic video scrolling">Ⅱ</button></div></div><div class="video-track" data-carousel-track data-autoplay="true">{video_cards}</div><p class="muted"><a class="text-link" href="{YOUTUBE_CHANNEL}" target="_blank" rel="noopener noreferrer">Visit the official YouTube channel</a></p></div></section>

  <section class="section home-reviews-section"><div class="container review-carousel" data-live-reviews-url="{REVIEWS_API}"><div class="section-head reveal"><div><p class="eyebrow">Patient feedback</p><h2>Words from our <span class="accent">Google reviewers</span></h2><p>Patient experiences from the clinic’s Google review feed. Select a card to read the full review.</p></div></div>{review_cards}<p class="muted review-feed-note" data-review-status aria-live="polite">Connecting to the clinic’s Google review feed…</p></div></section>

  <section class="section home-tradition-section"><div class="container home-tradition-grid"><div class="tradition-copy reveal"><p class="eyebrow">Siddha tradition</p><h2>Concept of Vatham, Pitham &amp; <span class="accent">Kabam</span></h2><p>Siddha tradition describes Vatham, Pitham, and Kabam as three principles used to discuss balance in health. This historical framework is part of Siddha practice; it does not replace medical testing or an individual clinical diagnosis.</p><div class="dosha-list"><article><strong>Vatham</strong><span>Traditionally associated with movement</span></article><article><strong>Pitham</strong><span>Traditionally associated with transformation</span></article><article><strong>Kabam</strong><span>Traditionally associated with structure</span></article></div></div><figure class="tradition-art reveal">{image_for(route, "wp-content/uploads/2026/02/ChatGPT-Image-Feb-25-2026-02_30_25-PM.png", "Traditional Siddha illustration of Vatham, Pitham, and Kabam")}</figure></div></section>

  {nasagra_section}

  <section class="section home-founder-section"><div class="container split-panel founder-panel"><div class="split-image reveal">{image_for(route, DOCTOR, HERO_ALT, "founder-image")}</div><div class="split-copy reveal"><p class="eyebrow">Founder &amp; Chief Siddha Consultant</p><h2>Dr. Sindhu <span class="accent">V.</span></h2><p>Dr. Sindhu V., B.S.M.S., M.D. (Siddha), H.A.H.M., Dip. Cupp., is the Founder and Chief Siddha Consultant at Siddha365 Health Care Clinic. Her practice is guided by Siddha knowledge, clinical assessment, and patient-centred conversations.</p><ul class="check-list"><li>Women’s health, fertility, and family care</li><li>Skin, hair, joint, and lifestyle concerns</li><li>Traditional therapies discussed as part of an individual plan</li></ul><a class="button button-secondary" href="about/">Meet the clinic and doctor</a></div></div></section>
<section class="section home-visit-section"><div class="container visit-planner"><div><p class="eyebrow">Make your visit easier</p><h2>A little preparation.<br><span class="accent">A clearer conversation.</span></h2><p>Keep your questions ready and contact the clinic before you travel.</p><a class="button" href="contact-us/">Plan your visit <span aria-hidden="true">↗</span></a></div><div class="visit-planner-details"><article><span class="visit-step-number">01</span><div><h3>Choose your location</h3><p>Villivakkam or Mogappair East, Chennai.</p><a class="text-link" href="contact-us/">Locations &amp; directions</a></div></article><article><span class="visit-step-number">02</span><div><h3>Confirm your appointment</h3><p>Call the clinic for availability and opening hours.</p><a class="text-link" href="tel:{PHONE_TEL}">{PHONE}</a></div></article><article><span class="visit-step-number">03</span><div><h3>Bring what matters</h3><p>Your previous reports, current medicine list and questions for the clinician.</p></div></article></div></div></section>
</main>'''
    return page_shell(route, "Home", "Siddha365 Health Care Clinic in Chennai. Explore individual treatment guides, meet Dr. Sindhu V, and plan a clinic visit.", body, homepage=True)


def treatment_index():
    route = "treatments"
    cards = "".join(condition_card(route, item) for item in CONDITIONS)
    body = f'''<main id="main-content"><section class="page-hero"><div class="container"><div class="page-hero-grid"><div class="reveal">{breadcrumb(route, "Treatments")}<p class="eyebrow">Individual care guides</p><h1>Treatments &amp; <span class="accent">areas of care</span></h1><p class="lead">Each topic opens a separate page with an overview of possible causes or purpose, common care options, and when to seek medical advice.</p></div>{image_for(route, DOCTOR, HERO_ALT, "page-hero-art reveal")}</div></div></section>
<section class="section"><div class="container"><div class="section-head"><div><p class="eyebrow">Browse by topic</p><h2>Choose a <span class="accent">care guide</span></h2><p>These pages are educational and do not diagnose or promise a cure. Please consult a qualified clinician for personal advice.</p></div></div><div class="card-grid">{cards}</div></div></section>
<section class="section-tight"><div class="container"><div class="section-head"><div><p class="eyebrow">Traditional practice</p><h2>Breathing and <span class="accent">mindful movement</span></h2></div></div><a class="nasagra-link reveal" href="../#nasagra-mudra">{image_for(route, "wp-content/uploads/2026/02/thepranabody.png", "Traditional illustration associated with pranayama concepts", "nasagra-link-image")}<span class="nasagra-link-copy"><span class="tag">Home learning guide</span><strong>Nasagra Mudra</strong><span>A traditional hand position used in alternate-nostril breathing, with general safety guidance.</span><span class="text-link">Read the practice guide on the home page</span></span></a></div></section></main>'''
    return page_shell(route, "Treatments", "Browse separate Siddha365 care guide pages for health conditions and traditional therapies.", body, section="treatments")


def condition_page(condition):
    slug = "treatments/" + condition["slug"]
    title = condition["title"]
    source_links = "".join(f'<a href="{esc(url)}" target="_blank" rel="noopener noreferrer">{esc(label)} ↗</a>' for label, url in condition["sources"])
    bullets = "".join(f"<li>{esc(item)}</li>" for item in condition["care"])
    figure = image_for(slug, condition["image"], condition.get("image_alt", title), "page-hero-art reveal")
    body = f'''<main id="main-content"><section class="page-hero"><div class="container"><div class="page-hero-grid"><div class="reveal">{breadcrumb(slug, title)}<p class="eyebrow">{esc(condition['category'])} · Care guide</p><h1>{esc(title)}</h1><p class="lead">{esc(condition['intro'])}</p></div>{figure}</div></div></section>
<section class="section"><div class="container condition-layout"><div class="condition-content">
  <section class="prose-panel reveal"><h2>What it is</h2><p>{esc(condition['intro'])}</p></section>
  <section class="prose-panel reveal"><h2>{'Why people may consider it' if condition['category'] == 'Traditional therapy' else 'How it may develop'}</h2><p>{esc(condition['why'])}</p></section>
  <section class="prose-panel reveal"><h2>Care and treatment options</h2><ul>{bullets}</ul></section>
  <section class="prose-panel reveal"><h2>Learn more</h2><div class="source-list">{source_links}</div></section>
  <p class="medical-note"><strong>Important:</strong> This page is general health information, not a diagnosis or personal treatment plan. Do not stop or replace prescribed care. Before starting Siddha medicines, supplements, or a procedure, discuss it with your treating clinician and share your complete medicines list.</p>
</div><aside class="care-aside reveal"><p class="eyebrow">Talk to the clinic</p><h2 class="care-aside-title">Discuss your next step</h2><p>Share your concern with the clinic and ask whether an appointment is appropriate.</p><a class="button" href="{WHATSAPP}" target="_blank" rel="noopener noreferrer">Message on WhatsApp ↗</a><div class="safety-note"><strong>When to get help</strong><br>{esc(condition['safety'])}</div></aside></div></section>
<section class="section-tight"><div class="container carousel-shell" data-carousel><div class="section-head"><div><p class="eyebrow">Explore more</p><h2>More areas of <span class="accent">care</span></h2></div><div class="carousel-actions"><a class="text-link" href="{rel(slug, 'treatments')}">All treatments</a><div class="carousel-controls"><button class="icon-button" type="button" data-carousel-prev aria-label="Scroll care guides left">←</button><button class="icon-button" type="button" data-carousel-next aria-label="Scroll care guides right">→</button><button class="icon-button" type="button" data-carousel-pause aria-pressed="false" aria-label="Pause automatic care guide scrolling">Ⅱ</button></div></div></div><div class="condition-track" data-carousel-track data-autoplay="true" role="region" aria-label="More areas of care">{"".join(condition_card(slug, item) for item in CONDITIONS if item['slug'] != condition['slug'])}</div></div></section></main>'''
    return page_shell(slug, title, condition["intro"], body, section="treatments")


def generic_page(route, title, eyebrow, intro, content, image=None, section=None):
    art = image_for(route, image, title, "page-hero-art reveal") if image else ""
    hero_class = "page-hero-grid" if image else ""
    hero = f'''<section class="page-hero"><div class="container"><div class="{hero_class}"><div class="reveal">{breadcrumb(route, title)}<p class="eyebrow">{esc(eyebrow)}</p><h1>{esc(title)}</h1><p class="lead">{esc(intro)}</p></div>{art}</div></div></section>'''
    body = f'<main id="main-content">{hero}{content}</main>'
    return page_shell(route, title, intro, body, section=section or route.split("/",1)[0])


def pages():
    output = {}
    output["index.html"] = homepage()
    output["treatments/index.html"] = treatment_index()
    for condition in CONDITIONS:
        route = "treatments/" + condition["slug"]
        output[route + "/index.html"] = condition_page(condition)

    about_content = f'''<section class="section"><div class="container split-panel"><div class="split-image reveal">{image_for("about", DOCTOR, HERO_ALT)}</div><div class="split-copy reveal"><p class="eyebrow">The clinic</p><h2>Traditional knowledge, delivered with <span class="accent">care and clarity</span></h2><p>Siddha365 Health Care Clinic is guided by Dr. Sindhu V., B.S.M.S., M.D. (Siddha), H.A.H.M., Dip. Cupp, Founder and Chief Siddha Consultant. The clinic offers Siddha consultations in Chennai with a focus on listening, individual assessment, and clear follow-up.</p><p>Care is discussed with attention to each person's history and current medicines. Patients are encouraged to ask questions, understand the limits of each option, and seek the right specialist care where needed.</p><ul class="check-list"><li>Women’s health, fertility, and family care</li><li>Skin, hair, joint, and lifestyle concerns</li><li>Traditional therapies discussed as part of an individual plan</li></ul><a class="button" href="{rel('about','contact-us')}">Clinic locations &amp; hours</a></div></div></section>
<section class="section-tight"><div class="container"><div class="feature-grid"><article class="feature-card"><span class="feature-icon" aria-hidden="true">◎</span><h3>Listen first</h3><p>Your concerns, goals, and medical history inform the conversation.</p></article><article class="feature-card"><span class="feature-icon" aria-hidden="true">✳</span><h3>Explain options</h3><p>Discuss what a treatment can and cannot do, along with alternatives.</p></article><article class="feature-card"><span class="feature-icon" aria-hidden="true">↗</span><h3>Work with your care team</h3><p>Share diagnoses and medicines so all clinicians can support safer decisions.</p></article></div></div></section>'''
    output["about/index.html"] = generic_page("about", "About Siddha365", "About us", "Meet the clinic and learn about the practitioner who leads Siddha365 Health Care Clinic.", about_content, DOCTOR, "about")

    treatment_images = [(c["image"], c["title"]) for c in CONDITIONS[:9]]
    treatment_images.extend([("wp-content/uploads/2024/07/oilslider-11-scaled.jpg", "Traditional oil therapy"), ("wp-content/uploads/2024/11/HERBAL-STEAM-BATH-scaled.jpg", "Herbal steam bath"), (DOCTOR, HERO_ALT)])
    gallery_items = "".join(f'<figure class="gallery-item reveal">{image_for("gallery", path, label)}<figcaption>{esc(label)}</figcaption></figure>' for path, label in treatment_images)
    gallery_content = f'<section class="section"><div class="container"><div class="gallery-grid">{gallery_items}</div><p class="medical-note">Clinic imagery is shared for general information. Individual treatment availability and suitability are decided after consultation.</p></div></section>'
    output["gallery/index.html"] = generic_page("gallery", "Clinic gallery", "At the clinic", "A look at Siddha365, traditional practice, and the clinic’s areas of care.", gallery_content, DOCTOR, "gallery")

    product_content = '''<section class="section"><div class="container"><div class="section-head"><div><p class="eyebrow">Medicine guidance</p><h2>Careful choices, <span class="accent">personal advice</span></h2><p>Products and medicines should be selected for the person, the condition, and the full medicines list—not as a one-size-fits-all purchase.</p></div></div><div class="product-grid"><article class="product-card"><span class="feature-icon" aria-hidden="true">✳</span><h3>Clinician guidance</h3><p>Discuss whether a medicine or product is suitable for your health concern and existing care plan.</p></article><article class="product-card"><span class="feature-icon" aria-hidden="true">◉</span><h3>Know the ingredients</h3><p>Ask what a product contains, how it is used, and whether it has known risks or interactions.</p></article><article class="product-card"><span class="feature-icon" aria-hidden="true">↗</span><h3>Follow up</h3><p>Report side effects or changing symptoms, and keep follow-up with your usual treating clinician.</p></article></div><div class="products-availability-cta"><a class="button" href="https://api.whatsapp.com/send/?phone=917845539622&amp;text=Hello%20Siddha%20365%2C%20I%20have%20a%20question%20about%20products.&amp;type=phone_number&amp;app_absent=0" target="_blank" rel="noopener noreferrer">Ask the clinic about availability ↗</a></div><p class="medical-note"><strong>Please note:</strong> This page does not offer online diagnosis or self-prescribing. Do not stop prescribed medicines or rely on product claims that promise a cure.</p></div></section>'''
    output["products/index.html"] = generic_page("products", "Products & medicine guidance", "Products", "Learn how to ask about Siddha medicine and product availability safely.", product_content, "wp-content/uploads/2026/02/new-doc.jpg", "products")

    review_cards = review_rows_html("reviews")
    reviews_content = f'''<section class="section"><div class="container review-carousel" data-live-reviews-url="{REVIEWS_API}"><div class="section-head"><div><p class="eyebrow">Patient feedback</p><h2>Latest Google <span class="accent">reviews</span></h2><p>Patient experiences from the clinic’s Google review feed. Select a card to read the full review.</p></div></div>{review_cards}<p class="muted review-feed-note" data-review-status aria-live="polite">Connecting to the clinic’s Google review feed…</p><div class="review-source-panel"><span class="source-mark" aria-hidden="true">G</span><div><h3>Shared on Google. Shown in their own words.</h3><p>Names, ratings and review text come from the clinic’s existing Google review feed. New feedback appears after that feed syncs with Google. Select a reviewer’s name to view their Google profile.</p></div></div></div></section>'''
    output["reviews/index.html"] = generic_page("reviews", "Google reviews", "Reviews", "Read patient feedback sourced from the clinic’s Google review feed.", reviews_content, None, "reviews")

    places = [
        ("Villivakkam", "No. 179, North Red Hills Road, near Subway, Villivakkam, Chennai, Tamil Nadu 600049."),
        ("Mogappair East", "No. 4/31, Pari Salai, Block 4, J.J. Nagar, Mogappair East, Chennai, Tamil Nadu 600037."),
    ]
    place_cards = "".join(f'''<article class="contact-card"><p class="eyebrow">Clinic {i}</p><h3>{esc(name)}</h3><p>{esc(address)}</p><a class="text-link" href="https://www.google.com/maps/search/?api=1&amp;query={esc(address.replace(' ', '+'))}" target="_blank" rel="noopener noreferrer">Directions on Google Maps</a></article>''' for i, (name, address) in enumerate(places, start=1))
    contact_content = f'''<section class="section"><div class="container"><div class="contact-grid">{place_cards}<article class="contact-card"><p class="eyebrow">Call or message</p><h3>Plan an appointment</h3><p>Contact the clinic with questions about availability or directions.</p><div class="hero-actions"><a class="button" href="tel:{PHONE_TEL}">Call {PHONE}</a><a class="button button-secondary" href="{WHATSAPP}" target="_blank" rel="noopener noreferrer">WhatsApp ↗</a></div></article><article class="contact-card" id="hours"><p class="eyebrow">Opening hours</p><h3>Clinic timings</h3><dl class="hours"><div><dt>Monday – Saturday</dt><dd>10:30 am – 1:30 pm</dd></div><div><dt>Evenings</dt><dd>7:00 pm – 9:30 pm</dd></div><div><dt>Sunday</dt><dd>By appointment</dd></div></dl></article></div><p class="medical-note">If you have a medical emergency, contact your local emergency service or go to the nearest emergency department.</p></div></section>'''
    output["contact-us/index.html"] = generic_page("contact-us", "Contact & clinic locations", "Visit Siddha365", "Find the Siddha365 Health Care Clinic locations in Villivakkam and Mogappair East, Chennai.", contact_content, DOCTOR, "contact-us")

    return output


def optimize_embedded_images(generated):
    """Create small WebP copies for local page images and rewrite their src URLs."""
    if Image is None:
        return generated

    image_src = re.compile(r'(<img\b[^>]*?\bsrc=")([^"]+)(")', re.IGNORECASE)
    optimized_dir = SITE / "assets" / "optimized"
    optimized_dir.mkdir(parents=True, exist_ok=True)
    outputs = {}

    for page_path, html in generated.items():
        page_dir = posixpath.dirname(page_path) or "."

        def replace_src(match):
            src = match.group(2)
            source_rel = posixpath.normpath(posixpath.join(page_dir, src))
            if not source_rel.startswith("wp-content/uploads/") or source_rel == DOCTOR:
                return match.group(0)
            source = SITE / Path(source_rel)
            if not source.is_file():
                return match.group(0)

            digest = hashlib.sha1(source_rel.encode("utf-8")).hexdigest()[:16]
            detailed_artwork = source_rel == "wp-content/uploads/2026/02/ChatGPT-Image-Feb-25-2026-02_30_25-PM.png"
            webp_rel = f"assets/optimized/{digest}-hq.webp" if detailed_artwork else f"assets/optimized/{digest}-v2.webp"
            optimized = SITE / Path(webp_rel)
            if webp_rel not in outputs:
                outputs[webp_rel] = optimized
                if not optimized.exists() or source.stat().st_mtime > optimized.stat().st_mtime:
                    with Image.open(source) as original:
                        image = ImageOps.exif_transpose(original)
                        image.thumbnail((1080, 1080), Image.Resampling.LANCZOS)
                        if "A" in image.getbands():
                            image = image.convert("RGBA")
                        else:
                            image = image.convert("RGB")
                        quality = 90 if detailed_artwork else 75
                        image.save(optimized, "WEBP", quality=quality, method=5)

            target = posixpath.relpath(webp_rel, page_dir)
            return f'{match.group(1)}{target}{match.group(3)}'

        optimized_html = image_src.sub(replace_src, html)

        def dimensions(match):
            tag = match.group(0)
            if re.search(r"\bwidth=", tag):
                return tag
            image_path = re.search(r'src="([^"]+)"', tag).group(1)
            if urlsplit(image_path).scheme:
                return tag
            local = SITE / posixpath.normpath(posixpath.join(page_dir, image_path))
            if not local.is_file():
                return tag
            with Image.open(local) as picture:
                width, height = picture.size
            return tag[:-1] + f' width="{width}" height="{height}">'

        generated[page_path] = re.sub(r'<img\b[^>]*>', dimensions, optimized_html)
    return generated


def build_distribution(generated):
    """Assemble a clean static deploy folder without the downloaded WordPress snapshot."""
    distribution = SITE / "dist"
    distribution.mkdir(exist_ok=True)
    published_paths = set(generated)

    for relative_path, content in generated.items():
        destination = distribution / Path(relative_path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(content, encoding="utf-8")

    # Copy only local files referenced by the generated HTML. This keeps source
    # snapshots, plugins, feeds, and XML-RPC discovery files out of the deploy.
    for page_path, content in generated.items():
        page_dir = posixpath.dirname(page_path)
        for match in re.finditer(r'\b(?:src|href)=["\']([^"\']+)["\']', content, re.IGNORECASE):
            candidate = match.group(1)
            parsed = urlsplit(candidate)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            raw_path = unquote(parsed.path).lstrip("/")
            local_path = posixpath.normpath(posixpath.join(page_dir, raw_path))
            if local_path.startswith("../") or local_path in published_paths:
                continue
            if local_path.endswith("/") and f"{local_path}index.html" in published_paths:
                continue
            source = SITE / Path(local_path)
            if not source.is_file():
                continue
            destination = distribution / Path(local_path)
            destination.parent.mkdir(parents=True, exist_ok=True)
            if local_path not in published_paths:
                shutil.copy2(source, destination)
                published_paths.add(local_path)

    security_headers = """/*
  Content-Security-Policy: default-src 'self'; base-uri 'self'; object-src 'none'; frame-ancestors 'none'; form-action 'self'; script-src 'self'; style-src 'self'; img-src 'self' https://i.ytimg.com; font-src 'self'; connect-src 'self' https://siddha365.com; frame-src https://www.youtube-nocookie.com https://maps.google.com https://www.google.com; upgrade-insecure-requests
  Referrer-Policy: strict-origin-when-cross-origin
  X-Content-Type-Options: nosniff
  X-Frame-Options: DENY
  Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=(), usb=(), autoplay=(self \"https://www.youtube-nocookie.com\")
"""
    (distribution / "_headers").write_text(security_headers, encoding="utf-8")
    apache_headers = '''<IfModule mod_headers.c>
  Header always set Content-Security-Policy "default-src 'self'; base-uri 'self'; object-src 'none'; frame-ancestors 'none'; form-action 'self'; script-src 'self'; style-src 'self'; img-src 'self' https://i.ytimg.com; font-src 'self'; connect-src 'self' https://siddha365.com; frame-src https://www.youtube-nocookie.com https://maps.google.com https://www.google.com; upgrade-insecure-requests"
  Header always set Referrer-Policy "strict-origin-when-cross-origin"
  Header always set X-Content-Type-Options "nosniff"
  Header always set X-Frame-Options "DENY"
  Header always set Permissions-Policy "camera=(), microphone=(), geolocation=(), payment=(), usb=(), autoplay=(self \\"https://www.youtube-nocookie.com\\")"
  Header always set Strict-Transport-Security "max-age=31536000"
  Header always unset X-Powered-By
</IfModule>
'''
    (distribution / ".htaccess").write_text(apache_headers, encoding="utf-8")
    (distribution / "robots.txt").write_text(
        "User-agent: *\nAllow: /\nSitemap: https://siddha365.com/sitemap.xml\n",
        encoding="utf-8",
    )
    urls = []
    for page_path in sorted(published_paths):
        if not page_path.endswith("index.html"):
            continue
        route = page_path[:-len("index.html")]
        urls.append(f"  <url><loc>{escape('https://siddha365.com/' + route)}</loc></url>")
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n'
    sitemap += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sitemap += "\n".join(urls) + "\n</urlset>\n"
    (distribution / "sitemap.xml").write_text(sitemap, encoding="utf-8")
    return len(published_paths)


def main():
    generated = optimize_embedded_images(pages())
    for relative_path, content in generated.items():
        destination = SITE / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(content, encoding="utf-8")
    distribution_files = build_distribution(generated)
    print(f"Generated {len(generated)} static pages and a clean distribution ({distribution_files} files) under {SITE / 'dist'}")


if __name__ == "__main__":
    main()
