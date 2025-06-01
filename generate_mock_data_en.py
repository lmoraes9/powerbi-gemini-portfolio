import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta

# Initialize Faker for English data
fake = Faker('en_US') # Explicitly set to English (US)

# --- Configuration ---
NUM_CAMPAIGNS = 50
NUM_USERS = 1500 # Slightly reduced for faster testing if needed
NUM_INTERACTIONS_TARGET = 15000
START_DATE_DATA = datetime(2022, 1, 1)

# --- English Sample Lists ---
positive_feedback_samples_en = [
    "Excellent service and quick turnaround!", "The platform is very user-friendly and efficient.",
    "Loved the quality of suppliers I found.", "Resolved my issue promptly, great support.",
    "Highly recommend this for sourcing.", "A fantastic tool for procurement.",
    "Easy to navigate and find what I need.", "My go-to for industrial parts.",
    "The RFQ process was smooth and effective.", "Top-notch experience overall."
]
negative_feedback_samples_en = [
    "The user interface is a bit clunky and hard to navigate.", "Response times from support were too slow.",
    "I had difficulty finding relevant suppliers for my specific niche.", "The pricing information isn't always clear.",
    "Not enough options for smaller businesses.", "The search results could be more accurate.",
    "Encountered a few bugs while submitting my RFQ.", "It's not as intuitive as I hoped.",
    "The verification process for suppliers seems lengthy.", "Expected a wider range of services."
]
neutral_feedback_samples_en = [
    "The platform works as expected.", "It's an okay tool for what it does.",
    "No major issues encountered during use.", "The service is standard, nothing exceptional.",
    "Met my basic requirements for sourcing.", "Average experience, did the job.",
    "The features are adequate for my needs.", "It's a functional platform."
]

rfq_request_samples_en = [
    "Requesting quote for 1,500 units of custom CNC machined aluminum (6061-T6) brackets, drawing #BRKT-003 attached. Need delivery by EOM.",
    "Seeking suppliers for ongoing fabrication of stainless steel (304L) enclosures, approx. 50 units/month. Detailed specs available.",
    "Urgent RFQ: 200 custom gears, material 4140 steel, hardened. Quote needed within 48 hours.",
    "Budgetary quote for injection molding of 10,000 ABS plastic casings, color black. Tooling to be discussed.",
    "Looking for sheet metal fabrication services: laser cutting and bending of 0.060\" mild steel. Qty: 500 pcs.",
    "Need a quote for 3D printing (SLA) of 10 prototype parts, material: durable resin. STL files provided.",
    "Sourcing for printed circuit board assembly (PCBA), 500 units, double-sided SMT. BOM and Gerbers attached.",
    "Inquiry for standard ball bearings, part number SKF-6205-2RS, quantity 1000. Best price and lead time."
]

supplier_capabilities_samples_en = [
    "Precision CNC Machining (3, 4 & 5-axis); Turning; Milling; Grinding; ISO 9001 Certified",
    "Plastic Injection Molding; Tooling Design & Fabrication; Overmolding; Insert Molding; Cleanroom Assembly",
    "Sheet Metal Fabrication; Laser Cutting; Turret Punching; Press Brake Forming; Welding (TIG, MIG); Powder Coating",
    "3D Printing Services (FDM, SLA, SLS, DMLS); Rapid Prototyping; Additive Manufacturing; Material Variety",
    "Electronic Contract Manufacturing (ECM); PCB Assembly (SMT, PTH); Cable Harnesses; Box Builds; Functional Testing",
    "Metal Stamping; Progressive Die; Deep Drawing; Secondary Operations; High Volume Production",
    "Custom Gear Manufacturing; Spur, Helical, Bevel Gears; Heat Treatment; Gear Hobbing & Shaping",
    "Industrial Fasteners & Hardware Distribution; Standard & Custom Components; Global Sourcing"
]

campaign_objectives_en = ['Lead Generation', 'Brand Awareness', 'Supplier Acquisition', 'User Engagement', 'Sales Conversion']
campaign_types_en = {
    'Paid Search': 'Google Ads', 'Paid Social': 'LinkedIn Ads', 'Content Marketing': 'SEO Blog',
    'Email Marketing': 'Email Drip', 'Webinar Series': 'Webinar Platform', 'Display Advertising': 'Display Network',
    'Industry Partnership': 'Partner Referral'
}
all_campaign_types_list_en = list(campaign_types_en.keys())
company_industries_en = ['Aerospace & Defense', 'Automotive Manufacturing', 'Medical Devices', 'General Industrial', 'Electronics & Semiconductors', 'Construction Equipment', 'Renewable Energy', 'Robotics & Automation']
company_sizes_en = ['Startup (1-10 emp)', 'Small Business (11-50 emp)', 'Medium Business (51-200 emp)', 'Large Company (201-1000 emp)', 'Enterprise (1000+ emp)']
countries_en = ['USA', 'Canada', 'United Kingdom', 'Germany', 'Mexico', 'Australia', 'India']
user_roles_buyer_en = ['Procurement Manager', 'Sourcing Specialist', 'Design Engineer', 'Operations Director', 'R&D Lead']
user_roles_supplier_en = ['Sales Director', 'Business Owner', 'Account Manager', 'Production Head']

# --- Generate campaign_details ---
print("Generating campaign_details_en.csv...")
campaign_data = []
for i in range(NUM_CAMPAIGNS):
    start_dt = fake.date_time_between(start_date=START_DATE_DATA, end_date='-1M')
    start_date = start_dt.date()
    end_date = None
    if random.random() > 0.2: # 80% have end dates
        end_dt = fake.date_time_between(start_date=start_dt + timedelta(days=random.randint(30, 180)), end_date='+3M')
        end_date = end_dt.date()

    campaign_type = random.choice(all_campaign_types_list_en)
    channel = campaign_types_en[campaign_type]
    budget = round(random.uniform(1000, 25000), 2)
    spend = round(random.uniform(0.6 * budget, budget), 2) if budget > 0 else 0
    if end_date and end_date < datetime.now().date(): # Past campaign
        spend = round(random.uniform(0.8 * budget, budget), 2)
    elif end_date and end_date >= datetime.now().date(): # Active campaign
        days_total = (end_date - start_date).days
        days_elapsed = (datetime.now().date() - start_date).days
        if days_total > 0 and days_elapsed > 0:
            spend = round(budget * min(1, (days_elapsed / days_total)) * random.uniform(0.7, 1.0), 2)
        elif days_elapsed <=0: # Not started yet
             spend = 0
        else: # Default to partial spend if dates are weird
            spend = round(random.uniform(0.3 * budget, 0.7*budget),2)
    spend = min(spend, budget)


    campaign_data.append({
        'campaign_id': f'CAMP{i+1:04d}',
        'campaign_name': f'{campaign_type} {start_date.year} {random.choice(["Alpha", "Bravo", "Charlie", "Delta"])}',
        'campaign_start_date': start_date,
        'campaign_end_date': end_date,
        'campaign_objective': random.choice(campaign_objectives_en),
        'campaign_type': campaign_type,
        'channel_source_primary': channel,
        'campaign_budget': budget,
        'campaign_spend': spend,
        'target_audience_segment': f'{random.choice(company_industries_en)} - {random.choice(company_sizes_en).split(" (")[0]}'
    })
df_campaigns = pd.DataFrame(campaign_data)
all_campaign_ids = df_campaigns['campaign_id'].tolist()

# --- Generate user_details ---
print("Generating user_details_en.csv...")
user_data = []
user_types = ['Buyer', 'Supplier', 'Prospect']

for i in range(NUM_USERS):
    reg_dt = fake.date_time_between(start_date=START_DATE_DATA, end_date='now')
    reg_date = reg_dt.date()
    user_type = random.choices(user_types, weights=[0.55, 0.35, 0.1], k=1)[0]
    role, company_name_val, industry, size_cat, sup_caps = None, None, None, None, None

    if user_type != 'Prospect':
        company_name_val = fake.company()
        industry = random.choice(company_industries_en)
        size_cat = random.choice(company_sizes_en)
        if user_type == 'Buyer':
            role = random.choice(user_roles_buyer_en)
        else: # Supplier
            role = random.choice(user_roles_supplier_en)
            sup_caps = random.choice(supplier_capabilities_samples_en) if random.random() < 0.85 else None

    is_paying = (user_type != 'Prospect' and random.random() < 0.5)
    ltv = round(random.uniform(200, 12000), 2) if is_paying else 0
    rfq_val_buyer = round(random.uniform(ltv * 0.3, ltv * 1.5),2) if user_type == 'Buyer' and is_paying else 0
    deals_val_supplier = round(random.uniform(ltv * 0.5, ltv * 2.5),2) if user_type == 'Supplier' and is_paying else 0

    feedback_text = None
    if random.random() < 0.3: # 30% of users leave feedback
        rand_feed = random.random()
        if rand_feed < 0.6: feedback_text = random.choice(positive_feedback_samples_en)
        elif rand_feed < 0.9: feedback_text = random.choice(negative_feedback_samples_en)
        else: feedback_text = random.choice(neutral_feedback_samples_en)

    first_touch_camp_id = random.choice(all_campaign_ids) if random.random() < 0.7 else None
    first_touch_channel = None
    if first_touch_camp_id:
        camp_info = df_campaigns[df_campaigns['campaign_id'] == first_touch_camp_id]
        if not camp_info.empty: first_touch_channel = camp_info['channel_source_primary'].iloc[0]
    if not first_touch_channel: first_touch_channel = random.choice(list(campaign_types_en.values()) + ['Organic Search', 'Direct'])


    user_data.append({
        'user_id': f'USER{i+1:05d}',
        'registration_date': reg_date,
        'first_touch_channel': first_touch_channel,
        'first_touch_campaign_id': first_touch_camp_id,
        'user_type': user_type,
        'user_role': role,
        'company_name': company_name_val,
        'company_industry': industry,
        'company_size_category': size_cat,
        'country': fake.country() if random.random() < 0.2 else random.choice(countries_en), # Mix of global and focus
        'supplier_capabilities_text': sup_caps,
        'user_feedback_text': feedback_text,
        'total_rfq_value_submitted_buyer': rfq_val_buyer,
        'total_deals_won_value_supplier': deals_val_supplier,
        'ltv_actual_or_predicted': ltv,
        'is_paying_customer': is_paying,
        'churn_date': fake.date_between(start_date=reg_date, end_date=reg_date + timedelta(days=random.randint(60,730))) if is_paying and random.random() < 0.1 else None
    })
df_users = pd.DataFrame(user_data)
user_ids_list = df_users['user_id'].tolist()

# --- Generate marketing_interactions ---
print("Generating marketing_interactions_en.csv...")
interaction_data = []
event_types = { # More granular event types
    'discovery': ['Site Visit', 'Blog Post View', 'Case Study View', 'Platform Search'],
    'consideration': ['Product Spec View', 'Supplier Profile View', 'Webinar Attended', 'Pricing Page Visit'],
    'conversion_buyer': ['General Inquiry Form', 'RFQ Submitted', 'Demo Request'],
    'conversion_supplier': ['Supplier Signup Start', 'Supplier Signup Complete', 'Paid Lead Purchase'],
    'engagement': ['Account Login', 'Saved Search', 'Favorite Item'],
    'ads_email': ['Ad Impression', 'Ad Click', 'Email Opened', 'Email Clicked']
}
all_event_names_list = [event for sublist in event_types.values() for event in sublist]
interaction_channels_list = list(campaign_types_en.values()) + ['Direct', 'Organic Search', 'Social Media Organic', 'Referral Site']
device_cats = ['Desktop', 'Mobile', 'Tablet']

interaction_id_counter = 0
session_id_counter = 0
current_timestamp_tracker = {} # To ensure interactions are chronological per user

for user_idx, user_row in df_users.iterrows():
    if interaction_id_counter >= NUM_INTERACTIONS_TARGET: break
    if user_idx % 100 == 0: print(f"  Generating interactions for user {user_idx+1}/{NUM_USERS}...")

    user_id = user_row['user_id']
    num_sessions = random.randint(1, 8)
    last_interaction_time_for_user = pd.to_datetime(user_row['registration_date'])
    current_timestamp_tracker[user_id] = last_interaction_time_for_user

    supplier_signup_started_session = False

for _ in range(num_sessions):
        if interaction_id_counter >= NUM_INTERACTIONS_TARGET: break
        session_id_counter += 1
        session_id = f'SESS{session_id_counter:07d}'
        num_events_in_session = random.randint(1, 7)

        # Define a data final para a geração da sessão (um pouco antes do agora)
        session_generation_end_limit = datetime.now() - timedelta(seconds=random.randint(1,60)) # Um pouco no passado

        # Calcula o início potencial da sessão
        potential_session_start = current_timestamp_tracker[user_id] + timedelta(minutes=random.randint(1, 60*3))

        # Garante que o início da sessão não ultrapasse o limite final de geração
        # E também que não seja antes da última interação do usuário
        actual_start_for_faker = max(current_timestamp_tracker[user_id] + timedelta(minutes=1), potential_session_start)
        
        # Garante que o datetime_start para o Faker não seja posterior ao datetime_end
        if actual_start_for_faker >= session_generation_end_limit:
            # Se o início calculado já passou do limite, ou está muito perto,
            # precisamos recuar o início ou pular esta sessão para este usuário,
            # ou simplesmente usar um intervalo muito pequeno se possível.
            # A opção mais segura para evitar o erro é garantir um intervalo válido.
            # Se a última interação do usuário já está muito perto do 'agora',
            # pode ser difícil gerar novas sessões para ele de forma realista no passado.

            # Se a última interação está muito perto do agora, dificilmente haverá novas sessões
            if current_timestamp_tracker[user_id] >= datetime.now() - timedelta(minutes=5): # Ex: se a última interação foi nos últimos 5 min
                 # print(f"Skipping session for user {user_id} as last interaction is too recent.")
                 continue # Pula para a próxima iteração do loop de sessões

            # Tenta criar um pequeno intervalo válido se possível, recuando o start
            actual_start_for_faker = max(
                current_timestamp_tracker[user_id] + timedelta(seconds=30), # Pelo menos 30s depois da última interação
                session_generation_end_limit - timedelta(minutes=random.randint(5,10)) # Alguns minutos antes do limite final
            )
            # Mais uma verificação para garantir que start < end
            if actual_start_for_faker >= session_generation_end_limit:
                # print(f"Still unable to create valid session time range for user {user_id}. Skipping session.")
                continue


        session_start_time = fake.date_time_between_dates(
            datetime_start=actual_start_for_faker,
            datetime_end=session_generation_end_limit
        )
        
        current_event_time = session_start_time



        for event_num in range(num_events_in_session):
            if interaction_id_counter >= NUM_INTERACTIONS_TARGET: break
            interaction_id_counter += 1

            event_name = random.choice(all_event_names_list)
            # Simple logic for supplier signup flow within a session
            if (user_row['user_type'] == 'Supplier' or (user_row['user_type'] == 'Prospect' and random.random() < 0.2)):
                if not supplier_signup_started_session and random.random() < 0.25 : # Chance to start
                    event_name = 'Supplier Signup Start'
                    supplier_signup_started_session = True
                elif supplier_signup_started_session and event_name != 'Supplier Signup Start' and random.random() < 0.5: # Chance to complete
                    event_name = 'Supplier Signup Complete'
                    supplier_signup_started_session = False # Reset for potential next session

            interaction_channel = random.choice(interaction_channels_list)
            campaign_for_interaction = None
            if interaction_channel in ['Google Ads', 'LinkedIn Ads', 'Email Drip', 'Display Network'] and random.random() < 0.6:
                campaign_for_interaction = random.choice(all_campaign_ids)

            interaction_value = 0
            interaction_details = None
            if event_name == 'RFQ Submitted':
                interaction_value = round(random.uniform(50, 15000), 2)
                interaction_details = random.choice(rfq_request_samples_en)
            elif event_name == 'Supplier Signup Complete':
                interaction_value = round(random.uniform(20, 200), 2) # Value of supplier lead
            elif 'View' in event_name:
                 interaction_details = f"Viewed: {fake.bs()} page"


            interaction_data.append({
                'interaction_id': f'INT{interaction_id_counter:07d}',
                'user_id': user_id,
                'session_id': session_id,
                'interaction_timestamp': current_event_time,
                'event_name': event_name,
                'channel_source_interaction': interaction_channel,
                'campaign_id': campaign_for_interaction,
                'device_category': random.choice(device_cats),
                'page_url_interaction': f'https://example.com/{fake.uri_path(deep=2)}',
                'is_conversion_event': any(event_name in conv_list for conv_list in [event_types['conversion_buyer'], event_types['conversion_supplier']]),
                'conversion_type': event_name if any(event_name in conv_list for conv_list in [event_types['conversion_buyer'], event_types['conversion_supplier']]) else None,
                'interaction_value': interaction_value,
                'interaction_details_text': interaction_details,
                'time_on_page_seconds': random.randint(5, 300) if 'View' in event_name else None
            })
            current_event_time += timedelta(seconds=random.randint(30, 300))
        current_timestamp_tracker[user_id] = current_event_time # Update last known time for user
        supplier_signup_started_session = False # Reset for next session


df_interactions = pd.DataFrame(interaction_data)

# Final check for duplicate interaction_ids (should not happen with counter)
if df_interactions['interaction_id'].duplicated().any():
    print("WARNING: Duplicate interaction_ids found after generation! This should not happen.")
    # Handle or raise error

# --- Save to CSV ---
df_campaigns.to_csv('campaign_details_en.csv', index=False, encoding='utf-8-sig')
df_users.to_csv('user_details_en.csv', index=False, encoding='utf-8-sig')
df_interactions.to_csv('marketing_interactions_en.csv', index=False, encoding='utf-8-sig')

print(f"\nGenerated {len(df_campaigns)} campaigns.")
print(f"Generated {len(df_users)} users.")
print(f"Generated {len(df_interactions)} interactions (target was {NUM_INTERACTIONS_TARGET}).")
print("Mock data generation in English completed!")