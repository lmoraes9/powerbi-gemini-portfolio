import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker()
# fake_BR = Faker('pt_BR')

# --- Configurações ---
NUM_CAMPAIGNS = 50
NUM_USERS = 2000
NUM_INTERACTIONS = 20000
START_DATE_DATA = datetime(2022, 1, 1)

# --- Listas de Exemplo para Novas Colunas ---
# ... (suas listas de keywords, rfq_samples, etc. permanecem aqui) ...
positive_feedback_keywords = ["excelente", "ótimo", "rápido", "eficiente", "fácil de usar", "adorei", "muito bom", "resolveu meu problema", "recomendo"]
negative_feedback_keywords = ["ruim", "lento", "difícil", "complicado", "péssimo", "não gostei", "problema", "decepcionado", "não funciona"]
neutral_feedback_keywords = ["ok", "razoável", "mediano", "funciona", "sem problemas", "normal", "esperado"]

rfq_request_samples = [
    "Preciso de cotação para 1000 peças usinadas em alumínio 6061, conforme desenho anexo.",
    "Solicito orçamento para fabricação de moldes de injeção para 3 componentes plásticos.",
    "Busco fornecedores para chapas de aço carbono, entrega em São Paulo.",
    "Cotação para 50 unidades de rolamentos axiais, especificações XPT-002.",
    "Procura-se serviço de prototipagem rápida em impressão 3D SLA para peças de teste.",
    "Necessito de cotação para 200 placas de circuito impresso, 4 camadas, com montagem de componentes."
]

supplier_capabilities_samples = [
    "Usinagem CNC; Torneamento; Fresamento",
    "Injeção Plástica; Ferramentaria",
    "Corte e Dobra de Chapas; Soldagem MIG/TIG",
    "Impressão 3D (FDM, SLA); Prototipagem",
    "Montagem Eletrônica (SMT, PTH); Testes Funcionais",
    "Fundição de Alumínio; Acabamento Superficial"
]

# --- Gerar Tabela campaign_details ---
# ... (código de df_campaigns permanece o mesmo) ...
print("Gerando campaign_details...")
campaign_data = []
campaign_objectives = ['Lead Generation', 'Brand Awareness', 'Supplier Acquisition', 'Engagement', 'Sales']
campaign_types_channels = {
    'Paid Search': 'Google Ads',
    'Paid Social': 'LinkedIn Ads',
    'Content Marketing': 'SEO',
    'Email Drip': 'Email',
    'Webinar': 'Webinar Platform',
    'Display Ads': 'Google Display Network',
    'Partnership': 'Referral Partner Site'
}
all_campaign_types = list(campaign_types_channels.keys())

for i in range(NUM_CAMPAIGNS):
    start_date_dt = fake.date_time_between(start_date=START_DATE_DATA, end_date='-1M')
    start_date = start_date_dt.date()
    end_date_option = None
    if random.random() > 0.3: # 70% das campanhas têm data de fim
        end_date_dt = fake.date_time_between(start_date=start_date_dt + timedelta(days=30), end_date='+6M')
        end_date_option = end_date_dt.date()

    campaign_type = random.choice(all_campaign_types)
    channel = campaign_types_channels[campaign_type]
    budget = round(random.uniform(500, 20000), 2)
    
    if end_date_option and end_date_option < datetime.now().date(): 
        spend = round(random.uniform(0.7 * budget, budget), 2) if budget > 0 else 0
    elif not end_date_option or end_date_option >= datetime.now().date(): 
        if not end_date_option: 
            total_duration_days = 365
        else:
            total_duration_days = (end_date_option - start_date).days
            total_duration_days = max(1, total_duration_days) 

        elapsed_duration_days = (datetime.now().date() - start_date).days
        elapsed_duration_days = max(0, min(elapsed_duration_days, total_duration_days))
        
        spend_ratio = random.uniform(0.7, 1.0) 
        spend = round(budget * (elapsed_duration_days / total_duration_days) * spend_ratio, 2)
        spend = min(spend, budget) 
    else:
        spend = 0

    campaign_data.append({
        'campaign_id': f'CAMP{i+1:04d}',
        'campaign_name': f'{random.choice(["Q1","Q2","Q3","Q4"])}_{start_date.year} {campaign_type} - {fake.bs().replace(" ","-")}',
        'campaign_start_date': start_date,
        'campaign_end_date': end_date_option,
        'campaign_objective': random.choice(campaign_objectives),
        'campaign_type': campaign_type,
        'channel_source_primary': channel,
        'campaign_budget': budget,
        'campaign_spend': spend,
        'target_audience_segment': random.choice(['Small CNC Shops US', 'Aerospace Buyers', 'Engineers - Material Selection', 'General Manufacturing LATAM', 'Industrial Procurement Managers'])
    })
df_campaigns = pd.DataFrame(campaign_data)
active_campaign_ids = df_campaigns[
    (df_campaigns['campaign_end_date'].isnull()) |
    (pd.to_datetime(df_campaigns['campaign_end_date']) >= datetime.now())
]['campaign_id'].tolist()
all_campaign_ids = df_campaigns['campaign_id'].tolist()


# --- Gerar Tabela user_details ---
# ... (código de df_users permanece o mesmo) ...
print("Gerando user_details...")
user_data = []
user_types = ['Buyer', 'Supplier', 'Prospect'] 
user_roles_buyer = ['Engineer', 'Procurement Manager', 'Designer', 'Operations Manager', 'R&D Specialist']
user_roles_supplier = ['Business Owner', 'Sales Rep', 'Marketing Manager', 'Production Manager']
company_industries = ['Aerospace & Defense', 'Automotive', 'Medical Devices', 'General Manufacturing', 'Electronics', 'Construction Equipment', 'Energy', 'Robotics & Automation']
company_sizes = ['Startup (1-10)', 'SMB (11-50)', 'Mid-Market (51-500)', 'Large Enterprise (501-2000)', 'Corporate (2000+)']
countries_focus = ['USA', 'Brazil', 'Mexico', 'Germany', 'China', 'Canada', 'India']

for i in range(NUM_USERS):
    reg_date_dt = fake.date_time_between(start_date=START_DATE_DATA, end_date='now')
    reg_date = reg_date_dt.date()
    user_type = random.choices(user_types, weights=[0.5, 0.3, 0.2], k=1)[0]
    role = None
    company_name_val = None
    company_industry_val = None
    company_size_val = None
    supplier_capability_val = None

    if user_type == 'Buyer':
        role = random.choice(user_roles_buyer)
        company_name_val = fake.company()
        company_industry_val = random.choice(company_industries)
        company_size_val = random.choice(company_sizes)
    elif user_type == 'Supplier':
        role = random.choice(user_roles_supplier)
        company_name_val = fake.company() + " " + random.choice(["Solutions", "Manufacturing", "Industries", "LLC", "Corp"])
        company_industry_val = random.choice(company_industries)
        company_size_val = random.choice(company_sizes)
        supplier_capability_val = random.choice(supplier_capabilities_samples) if random.random() < 0.8 else None

    is_paying = False
    ltv = 0
    total_rfq_value = 0
    total_deals_value = 0 

    if user_type == 'Buyer' and random.random() < 0.4:
        is_paying = True 
        ltv = round(random.uniform(500, 15000), 2)
        total_rfq_value = round(random.uniform(ltv * 0.5, ltv * 2),2)
    if user_type == 'Supplier' and random.random() < 0.6:
        is_paying = True 
        ltv = round(random.uniform(1000, 20000), 2)
        total_deals_value = round(random.uniform(ltv * 0.8, ltv * 3),2) 

    first_touch_camp_id = random.choice(all_campaign_ids) if random.random() < 0.8 else None
    first_touch_channel_val = None
    if first_touch_camp_id:
        campaign_info = df_campaigns[df_campaigns['campaign_id'] == first_touch_camp_id]
        if not campaign_info.empty:
            first_touch_channel_val = campaign_info['channel_source_primary'].iloc[0]
    if not first_touch_channel_val:
         first_touch_channel_val = random.choice(list(campaign_types_channels.values()) + ['Organic Search', 'Direct'])

    feedback_text_val = None
    mock_sentiment_score = None 
    if random.random() < 0.25: 
        if random.random() < 0.6: 
            feedback_text_val = f"{random.choice(positive_feedback_keywords).capitalize()}! {fake.sentence(nb_words=random.randint(5,15))}"
            mock_sentiment_score = round(random.uniform(0.5, 1.0), 2)
        elif random.random() < 0.75: 
            feedback_text_val = f"{random.choice(negative_feedback_keywords).capitalize()}. {fake.sentence(nb_words=random.randint(5,15))}"
            mock_sentiment_score = round(random.uniform(0.0, 0.49), 2)
        else: 
            feedback_text_val = f"{random.choice(neutral_feedback_keywords).capitalize()}, {fake.sentence(nb_words=random.randint(5,10))}"
            mock_sentiment_score = round(random.uniform(0.4, 0.6), 2)

    user_data.append({
        'user_id': f'USER{i+1:05d}',
        'registration_date': reg_date,
        'first_touch_channel': first_touch_channel_val,
        'first_touch_campaign_id': first_touch_camp_id,
        'user_type': user_type,
        'user_role': role,
        'company_name': company_name_val,
        'company_industry': company_industry_val,
        'company_size_category': company_size_val,
        'supplier_capabilities_text': supplier_capability_val, 
        'country': random.choice(countries_focus),
        'region': fake.state() if random.random() < 0.7 else None, 
        'total_rfq_value_submitted_buyer': total_rfq_value if user_type == 'Buyer' else 0,
        'total_deals_won_value_supplier': total_deals_value if user_type == 'Supplier' else 0,
        'ltv_actual_or_predicted': ltv,
        'is_paying_customer': is_paying,
        'churn_date': fake.date_between(start_date=reg_date, end_date=reg_date + timedelta(days=random.randint(90, 730))) if is_paying and random.random() < 0.15 else None,
        'user_feedback_text': feedback_text_val, 
        'mock_sentiment_score': mock_sentiment_score 
    })
df_users = pd.DataFrame(user_data)
user_ids_list = df_users['user_id'].tolist()


# ############################################################################
# ## DEFINIÇÃO DA FUNÇÃO create_interaction_entry MOVIDA PARA CIMA ########
# ############################################################################
# Função auxiliar para criar entrada de interação (para reduzir repetição)
def create_interaction_entry(ic_counter, u_id, s_id, ts, evt_name, u_row, camps_df, act_camp_ids, all_camp_ids, cc_map, int_chans, utm_s_map, utm_m_map, dev_cats, fk, event_names_conversion_buyer_list, event_names_conversion_supplier_list, event_names_ads_email_list):
    interaction_channel = random.choice(int_chans)
    campaign_for_interaction = None
    if interaction_channel in ['Google Ads', 'LinkedIn Ads', 'Email', 'Referral Partner Site'] and len(act_camp_ids) > 0 and random.random() < 0.7:
        campaign_for_interaction = random.choice(act_camp_ids)
    elif random.random() < 0.1 and len(all_camp_ids) > 0: 
        campaign_for_interaction = random.choice(all_camp_ids)

    is_conversion = evt_name in event_names_conversion_buyer_list or evt_name in event_names_conversion_supplier_list
    conversion_type_val = evt_name if is_conversion else None
    interaction_value_val = 0
    interaction_details_val = None 

    if evt_name == 'RFQ Submitted':
        interaction_value_val = round(random.uniform(100, 20000), 2)
        interaction_details_val = random.choice(rfq_request_samples) + f" (Priority: {random.choice(['High', 'Medium', 'Low'])})"
    elif evt_name == 'Supplier Signup Complete':
        interaction_value_val = round(random.uniform(50, 500), 2) 
        interaction_details_val = f"Supplier signed up. Profile completeness: {random.randint(40,100)}%."
    elif evt_name == 'Lead Form Submit (General Inquiry)':
        interaction_details_val = f"User inquired about: {fk.bs()}. Contact preference: {random.choice(['Email', 'Phone'])}."
    elif 'Content View' in evt_name:
        interaction_details_val = f"Time spent on content: {random.randint(30, 300)}s. Scrolled to {random.randint(20,100)}%."

    utm_campaign_val = None
    utm_source_val = None
    utm_medium_val = None

    if campaign_for_interaction:
        camp_info = camps_df[camps_df['campaign_id'] == campaign_for_interaction]
        if not camp_info.empty:
            utm_campaign_val = camp_info['campaign_name'].iloc[0].replace(" ","_").lower()
            primary_channel = camp_info['channel_source_primary'].iloc[0]
            utm_source_val = utm_s_map.get(primary_channel)
            utm_medium_val = utm_m_map.get(primary_channel)

    if not utm_source_val: 
        if interaction_channel == 'Organic Search':
            utm_source_val = 'google' 
            utm_medium_val = 'organic'
        elif interaction_channel == 'Direct':
            utm_source_val = '(direct)'
            utm_medium_val = '(none)'
        elif interaction_channel == 'Organic Social':
            utm_source_val = random.choice(['linkedin', 'facebook_page', 'twitter_profile'])
            utm_medium_val = 'social_organic'
        elif interaction_channel == 'Referral':
            utm_source_val = fk.domain_name()
            utm_medium_val = 'referral'
        else: 
            utm_source_val = interaction_channel.lower().replace(" ", "_")
            utm_medium_val = 'earned' if interaction_channel == 'SEO' else 'platform_feature'

    page_path = fk.uri_path()
    if evt_name in cc_map:
        page_path = cc_map[evt_name].lower().replace(" ", "-") + "/" + (fk.slug() if cc_map[evt_name] not in ['RFQ Form', 'Supplier Signup Page', 'Supplier Signup Confirmation'] else "")

    return {
        'interaction_id': f'INT{ic_counter:07d}',
        'user_id': u_id,
        'session_id': s_id,
        'interaction_timestamp': ts,
        'event_name': evt_name,
        'channel_source_interaction': interaction_channel,
        'campaign_id': campaign_for_interaction,
        'ad_group_name': f'AdGroup_{fk.word().capitalize()}' if 'Ad' in evt_name or 'Ads' in interaction_channel else None,
        'ad_creative_name': f'Creative_{random.randint(1,5)}' if 'Ad' in evt_name or 'Ads' in interaction_channel else None,
        'keyword_text': fk.word() + ((" " + fk.word()) if random.random() > 0.5 else "") if 'Search' in interaction_channel or 'Search' in evt_name else None,
        'content_title': f'{cc_map.get(evt_name, "Generic Page")} - {fk.catch_phrase()}' if 'Content View' in evt_name or 'Product Page View' in evt_name or 'Site Visit' in evt_name else None,
        'content_category': cc_map.get(evt_name, None),
        'device_category': random.choice(dev_cats),
        'page_url_interaction': f'https://www.thomasnet.com/{page_path}',
        'referrer_url_interaction': f'https://{fk.domain_name()}/{fk.uri_path()}' if random.random() < 0.6 else None,
        'is_conversion_event': is_conversion,
        'conversion_type': conversion_type_val,
        'interaction_value': interaction_value_val,
        'interaction_details_text': interaction_details_val, 
        'utm_source': utm_source_val,
        'utm_medium': utm_medium_val,
        'utm_campaign': utm_campaign_val,
        'utm_content': f'content_variant_{random.choice(["A","B","C"])}' if utm_medium_val not in ['(none)','organic', 'referral'] and utm_campaign_val else None,
        'utm_term': fk.word() if utm_medium_val == 'cpc' else None, 
        'time_on_page_seconds': random.randint(10, 600) if evt_name not in event_names_ads_email_list else None,
        'scroll_depth_percent': random.randint(10,100) if evt_name not in event_names_ads_email_list else None
    }
# ############################################################################
# ## FIM DA DEFINIÇÃO DA FUNÇÃO MOVIDA #####################################
# ############################################################################


# --- Gerar Tabela marketing_interactions ---
print("Gerando marketing_interactions...")
interaction_data = []
# Eventos de Funil e Engajamento
event_names_discovery = ['Site Visit', 'Content View (Blog)', 'Content View (Case Study)', 'Search Performed (Platform)']
event_names_consideration = ['Product Page View', 'Supplier Profile View', 'Webinar Attended', 'Pricing Page View']
event_names_conversion_buyer = ['Lead Form Submit (General Inquiry)', 'RFQ Submitted', 'Demo Request']
event_names_conversion_supplier = ['Supplier Signup Start', 'Supplier Signup Complete', 'Supplier Lead Purchase'] 
event_names_engagement = ['Account Login', 'Saved Search Alert Created', 'Added to Favorites (Supplier/Product)']
event_names_ads_email = ['Ad Impression', 'Ad Click', 'Email Open', 'Email Click']

all_event_names = (event_names_discovery + event_names_consideration +
                   event_names_conversion_buyer + event_names_conversion_supplier +
                   event_names_engagement + event_names_ads_email)

interaction_channels = list(campaign_types_channels.values()) + ['Direct', 'Referral', 'Organic Search', 'Organic Social']
device_categories = ['Desktop', 'Mobile', 'Tablet']
utm_sources_map = {'Google Ads': 'google', 'LinkedIn Ads': 'linkedin', 'Facebook Ads': 'facebook', 'Email': 'newsletter', 'Referral Partner Site': 'partner_site'} 
utm_mediums_map = {'Google Ads': 'cpc', 'LinkedIn Ads': 'social_paid', 'Facebook Ads': 'social_paid', 'SEO': 'organic', 'Email': 'email', 'Referral Partner Site':'referral', 'Webinar Platform':'webinar'}

content_categories_map = {
    'Content View (Blog)': 'Blog Post',
    'Content View (Case Study)': 'Case Study',
    'Product Page View': 'Product Specification',
    'Supplier Profile View': 'Supplier Profile',
    'RFQ Submitted': 'RFQ Form',
    'Supplier Signup Start': 'Supplier Signup Page',
    'Supplier Signup Complete': 'Supplier Signup Confirmation',
    'Site Visit': 'Homepage' 
}

event_weights = [
    0.15, 0.10, 0.05, 0.08, 
    0.10, 0.07, 0.03, 0.04, 
    0.03, 0.04, 0.02,       
    0.03, 0.02, 0.01,       
    0.05, 0.02, 0.02,       
    0.05, 0.03, 0.03, 0.03  
]
total_weight = sum(event_weights)
event_weights = [w / total_weight for w in event_weights]

interaction_counter = 0
session_id_counter = 0
# Adicionei uma variável para rastrear o último timestamp de interação globalmente para evitar problemas de lógica temporal.
# last_interaction_time_overall = START_DATE_DATA # Inicializa com a data de início dos dados.
# Ou melhor, rastrear por usuário:
last_interaction_time_per_user = {}


for user_idx, user_row in df_users.iterrows(): 
    if interaction_counter >= NUM_INTERACTIONS:
        break
    if user_idx % 100 == 0:
        print(f"Gerando interações para usuário {user_idx}...")

    user_id = user_row['user_id']
    user_reg_date = pd.to_datetime(user_row['registration_date'])
    num_sessions_for_user = random.randint(1, 10) 
    supplier_signup_started_for_user = False

    current_user_last_interaction_time = last_interaction_time_per_user.get(user_id, user_reg_date)


    for _ in range(num_sessions_for_user):
        if interaction_counter >= NUM_INTERACTIONS:
            break
        session_id_counter += 1
        session_id = f'SESS{session_id_counter:08d}'
        num_events_in_session = random.randint(1, 8)
        
        # A primeira interação da sessão deve ser após o registro do usuário e após a última interação desse usuário
        min_start_time_session = max(user_reg_date, current_user_last_interaction_time + timedelta(minutes=random.randint(5, 60*6))) # Próxima sessão algum tempo depois

        # Garante que a sessão ocorra entre o min_start_time_session e 'agora'
        # Adiciona um pequeno delta para garantir que start_date seja menor que end_date em fake.date_time_between
        if min_start_time_session >= datetime.now() - timedelta(seconds=1):
            # Se o min_start_time já é basicamente 'agora' ou no futuro, podemos pular ou ajustar.
            # Para simplificar, vamos avançar um pouco o tempo base do usuário se necessário
            # ou apenas usar o registration_date se for um usuário novo sem interações.
            if current_user_last_interaction_time == user_reg_date: # Novo usuário, sem interações prévias
                 start_ts_session = fake.date_time_between(start_date=user_reg_date, end_date='now')
            else: # Usuário já teve interações, mas a próxima seria no futuro
                 # Aqui, poderíamos decidir não gerar mais sessões para este usuário neste run, ou
                 # artificialmente limitar o timestamp. Por ora, vamos tentar prender ao 'now'.
                 start_ts_session = fake.date_time_between(start_date=max(user_reg_date, datetime.now() - timedelta(days=10)), end_date='now')
        else:
            start_ts_session = fake.date_time_between(
                start_date=min_start_time_session,
                end_date=datetime.now() 
            )
        current_timestamp = start_ts_session


        for event_num_in_session in range(num_events_in_session):
            if interaction_counter >= NUM_INTERACTIONS:
                break
            
            chosen_event_name = random.choices(all_event_names, weights=event_weights, k=1)[0]

            if user_row['user_type'] == 'Supplier' or (user_row['user_type'] == 'Prospect' and random.random() < 0.3): 
                if not supplier_signup_started_for_user and random.random() < 0.15: 
                    chosen_event_name = 'Supplier Signup Start'
                    supplier_signup_started_for_user = True
                elif supplier_signup_started_for_user and chosen_event_name != 'Supplier Signup Start' and random.random() < 0.4: 
                    chosen_event_name = 'Supplier Signup Complete'
            
            if chosen_event_name == 'Supplier Signup Complete' and not supplier_signup_started_for_user and event_num_in_session < num_events_in_session -1 :
                 entry_start = create_interaction_entry( 
                    interaction_counter, user_id, session_id, current_timestamp, 'Supplier Signup Start',
                    user_row, df_campaigns, active_campaign_ids, all_campaign_ids, 
                    content_categories_map, interaction_channels, utm_sources_map, utm_mediums_map, device_categories, fake,
                    event_names_conversion_buyer, event_names_conversion_supplier, event_names_ads_email # Passando as listas
                 )
                 interaction_data.append(entry_start)
                 interaction_counter +=1
                 current_timestamp += timedelta(minutes=random.randint(1, 5)) 
                 if interaction_counter >= NUM_INTERACTIONS: break

            entry = create_interaction_entry(
                interaction_counter, user_id, session_id, current_timestamp, chosen_event_name,
                user_row, df_campaigns, active_campaign_ids, all_campaign_ids,
                content_categories_map, interaction_channels, utm_sources_map, utm_mediums_map, device_categories, fake,
                event_names_conversion_buyer, event_names_conversion_supplier, event_names_ads_email # Passando as listas
            )
            interaction_data.append(entry)
            
            interaction_counter += 1
            current_user_last_interaction_time = current_timestamp # Atualiza o último timestamp da interação PARA ESTE USUÁRIO
            current_timestamp += timedelta(minutes=random.randint(1, 15)) 
    
    last_interaction_time_per_user[user_id] = current_user_last_interaction_time # Guarda o último timestamp para este usuário


df_interactions = pd.DataFrame(interaction_data)

# --- Salvar em CSV ---
df_campaigns.to_csv('campaign_details.csv', index=False)
df_users.to_csv('user_details.csv', index=False)
df_interactions.to_csv('marketing_interactions.csv', index=False)

print("Dados gerados e salvos em CSV!")
# ... (código de print e checagem do funil permanece o mesmo) ...
print(f"df_campaigns: {len(df_campaigns)} linhas, {df_campaigns.shape[1]} colunas")
print(f"df_users: {len(df_users)} linhas, {df_users.shape[1]} colunas")
print(f"df_interactions: {len(df_interactions)} linhas, {df_interactions.shape[1]} colunas")

supplier_starts = df_interactions[df_interactions['event_name'] == 'Supplier Signup Start']['user_id'].nunique()
supplier_completes = df_interactions[df_interactions['event_name'] == 'Supplier Signup Complete']['user_id'].nunique()
print(f"\nUsuários únicos com 'Supplier Signup Start': {supplier_starts}")
print(f"Usuários únicos com 'Supplier Signup Complete': {supplier_completes}")

if supplier_starts > 0:
    users_started = set(df_interactions[df_interactions['event_name'] == 'Supplier Signup Start']['user_id'])
    users_completed = set(df_interactions[df_interactions['event_name'] == 'Supplier Signup Complete']['user_id'])
    users_did_both = len(users_started.intersection(users_completed))
    print(f"Usuários únicos que iniciaram E completaram o signup de supplier: {users_did_both}")
    if users_did_both > 0 : # Evitar divisão por zero se ninguém completou e iniciou
         print(f"Taxa de conclusão do funil de supplier (simplificada): {users_did_both/supplier_starts:.2%}")
    else:
        print(f"Taxa de conclusão do funil de supplier (simplificada): 0.00%")