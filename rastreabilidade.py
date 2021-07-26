import streamlit as st
from streamlit import caching
import pandas as pd
from io import StringIO
import numpy as np
from itertools import cycle
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, JsCode
import streamlit.components.v1 as components
import base64
import json
import smtplib
import time
import datetime
import time
from datetime import date, datetime, time
import pytz

from google.cloud import firestore
from google.oauth2 import service_account

######################################################################################################
# Configurações da página
######################################################################################################

st.set_page_config(
    page_title="Rastreabilidade",
    layout="wide",
)

######################################################################################################
# Configurando acesso ao firebase
######################################################################################################
textkey_2 = """{\n  \"type\": \"service_account\",\n  \"project_id\": \"lid-rastr\",\n  \"private_key_id\": \"a7c22fdbd57a9b70915020a3075fe968298d9b07\",\n  \"private_key\": \"-----BEGIN PRIVATE KEY-----\\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDGij/1qDDBibyf\\nooQJBsT+afWbqJchuhDgLixrMMrBknCzDKqnMKQGPAq3d3E5A95vf0tyJOQflefW\\ntb89OApzGmx9fDzN4NKIgUPQZJYB1GG/x+JeyQqJCVPzpG3R5t6WtK7XSWxg5WBx\\nQ1JS2KAYKZehZzhp1zDr25w5LeQlNpIbKpAS67yOO4nieA3ft5XGF/YCTPBA5IrV\\nkPusIUE0nbFGPIqHnq6Cj3pnVzpd/iweec9UiGVeUCW3Dw7kCJQom1lHoVYksMhx\\nZSQGzAiIOu6s4OLE/CPXpoa6P8i2erppcQyYIXJ6dL2W4AJ/CKKAt0zRN1N13pgt\\nnhpUIXELAgMBAAECggEAQ8JlR9MKKNN4Y8cUZvw/eVDyeRiV0/Xr0ocPs9moKV5w\\nRjt5dqwcHuCZC7qhEsNmRAle12sNzFXeFSJcTWl174jCJCWlnuIvGFV9rn7Vz3QL\\nlGeEs7LLfK+JTmr87BluOGMcFO/DJGLEgoNmck3qfbScQoK29zBxSt3duIoYBja5\\n6MmkTPPnQhi/gWiI7V/vsAcLvSQH1+PqYP/OzzIsd/Cp9vwNx/u+i50AndsXjDUR\\n2HcfwOIeE3h4H3Zh1Fvzgsznm2fjKEOJAG6wzJtzbe0mBRslld2v+Wuy3QuDM1+N\\nDA1hvSatnxaLNfGCnA70YmDoe+ueoVcGdUl2u0NbYQKBgQD7F/GUeV6Zp/ouh7Ka\\nzmtAtJDk5nWy43ujHH/E+0v5jqz/W0RbvAYuK321IyN1wBA/LHqHMit3Z+XxEw9Z\\ndKGEASNY1Lv7HEgoks6Chn02+k9HJLYD0sdQgIzhMKrIP5UOmwDQT+BNv+nWKXhn\\nyrmwyPnNZ8M2e2+hJBt6dceg2wKBgQDKa2pebKAq7DT0XeU6x6vX/kGtBCycgvzn\\nKb7R9Z7QnUk0IAfAUtQ0wwclhi1R08XpZwzL3BEO6EAo5fzJa/6ObEv9SUwsx7YP\\nriekUDkGqxacGFIe7QqVEHxQgDQ0eUrGd6SOELGNOmi5etVZJlsMZKp6GmvyQL8n\\nbMQUqS+PkQKBgQCnRZUnLw+JV3EATF/8ZyTmDyQziR/Bk3ALAnJPvIUpdBXla1yH\\nrCOF4G03HXiC+fcYzr21kQOJ4Uo6plLkaiErOkLc66NrLrUXam1uYL/Lv0bPAzLK\\nK0GibHDtl6k+C7V17GbHX17zDLVveWL/6fp4PfrEDqrqgaKk+9PeadYaXwKBgG6m\\nczn0pUVxY60lWrZcCesDeQFMI9rWm8r9fesmGk+teyO8UqBmZswExHZVt5ZgbnKd\\nO1iBDu4YNWJl/l5Y44kVWCC4HaTo8vP1XoQqulGT2sMvZEy1hTBhF6OlwWPh3edJ\\n5bEnHPe3syGZLOET33eR28LtiI6fqB60DSfCKFaRAoGAR74hITKw+PbTdUWql/uT\\nuVHE1JaxhnvNRc+/khoNp903fGAHiVJ5hjnFKRVRUB8uMUtTSfKsS9Y5a4BatvB+\\nAdAY/BHdXad2Xwom8kH9Oirph8exXro3x+FmFzBbwcRwggCGXPX0p1vPPzcZLWnp\\nEXk80T6vA2vVQxYvIrG1yqw=\\n-----END PRIVATE KEY-----\\n\",\n  \"client_email\": \"firebase-adminsdk-i3gy3@lid-rastr.iam.gserviceaccount.com\",\n  \"client_id\": \"105084896569014155165\",\n  \"auth_uri\": \"https://accounts.google.com/o/oauth2/auth\",\n  \"token_uri\": \"https://oauth2.googleapis.com/token\",\n  \"auth_provider_x509_cert_url\": \"https://www.googleapis.com/oauth2/v1/certs\",\n  \"client_x509_cert_url\": \"https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-i3gy3%40lid-rastr.iam.gserviceaccount.com\"\n}\n"""

# Pega as configurações do banco do segredo
key_dict = json.loads(textkey_2)
creds = service_account.Credentials.from_service_account_info(key_dict)

# Seleciona o projeto
db = firestore.Client(credentials=creds, project="lid-rastr")

# Ajustando fuso

tz = pytz.timezone('America/Bahia')

###########################################################################################################################################
#####                    			funcoes                                                                            #########
###########################################################################################################################################

# Define cores para os valores validos ou invalidos
def color(val):
    if val == 'invalido':
        color = 'red'
    else:
        color = 'white'
    return 'background-color: %s' % color

# leitura de dados do banco
@st.cache(allow_output_mutation=True)
def load_colecoes(colecao, colunas, colunas_pal, tipo):
    # dicionario vazio
    dicionario = {}
    index = 0

    # Define o caminho da coleção do firebase
    posts_ref = db.collection(colecao)

    # Busca todos os documentos presentes na coleção e salva num dataframe
    for doc in posts_ref.stream():
        dic_auxiliar = doc.to_dict()
        dicionario[str(index)] = dic_auxiliar
        if tipo == 1:
            dicionario[str(index)]['documento'] = doc.id
        if tipo == 0:
            dicionario[str(index)]['documento'] = doc.id
        index += 1
    # Transforma o dicionario em dataframe
    df = pd.DataFrame.from_dict(dicionario)

    # troca linhas com colunas
    df = df.T
    df2 = pd.DataFrame(columns=colunas_pal)

    # Bobinas
    if (tipo == 0) and (df.shape[0] > 0):
        # Transforma string em tipo data

        df['data'] = pd.to_datetime(df['data'])

        # Ordena os dados pela data
        df = df.sort_values(by=['data'], ascending=False)

        # Remove o index
        df = df.reset_index(drop=True)

        for index, row in df.iterrows():
            csv = str(row['Paletes'])
            csv_string = StringIO(csv)
            df_aux = pd.read_table(csv_string, sep=',')
            df2 = df2.append(df_aux, ignore_index=True)

        # Ordena as colunas
        df = df[colunas]
        df2 = df2[colunas_pal]

    # selante
    if (tipo == 1) and (df.shape[0] > 0):
        # Transforma string em tipo data

        df['data'] = pd.to_datetime(df['data'])

        # Ordena os dados pela data
        df = df.sort_values(by=['data'], ascending=False)

        # Remove o index
        df = df.reset_index(drop=True)

        for index, row in df.iterrows():
            csv = str(row['Paletes'])
            csv_string = StringIO(csv)
            df_aux = pd.read_table(csv_string, sep=',')
            df2 = df2.append(df_aux, ignore_index=True)

        # Ordena as colunas
        df = df[colunas]
        df2 = df2[colunas_pal]

    return df, df2

def adicionar_bobina():
    # Formulario para inclusao de bobinas
    dic = {}

    # Dados das bobinas
    with st.form('forms_Bobina'):
        dic['status'] = 'Disponível'
        dic['data'] = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
        s1, s2, s3, s4, s5, s6 = st.beta_columns([2, 2, 2, 2, 2, 1])
        dic['numero_OT'] = s1.text_input('Número OT')
        dic['tipo_bobina'] = s2.text_input('Tipo da bobina')
        dic['codigo_bobina'] = s3.text_input('Codigo da bobina')
        dic['peso_bobina'] = s4.number_input('Peso da bobina', step=1, format='%i', value=9000)
        dic['codigo_SAP'] = s5.text_input('Código SAP')
        dic['data_entrada'] = ''
        submitted = s6.form_submit_button('Adicionar bobina ao sistema')

    if submitted:

        # Transforma dados do formulário em um dicionário
        keys_values = dic.items()
        new_d = {str(key): str(value) for key, value in keys_values}

        # Verifica campos não preenchidos e os modifica
        for key, value in new_d.items():
            if (value == '') or value == '[]':
                new_d[key] = '-'

        # define a quantidade de paletes gerados pela bobina
        new_d['paletes_gerados'] = int(int(new_d['peso_bobina']) * 412 / 187200)

        # Define a quantidade de paletes que podem ser gerados pela bobina
        qtd_paletes = int(new_d['paletes_gerados'])

        # cria dataframe e preenche com os dados da bobina
        df_paletes_sem = pd.DataFrame(columns=col_pal_sem, index=list(range(qtd_paletes)))
        df_paletes_sem['numero_OT'] = str(new_d['numero_OT'])
        df_paletes_sem['tipo_tampa'] = str(new_d['tipo_bobina'])
        df_paletes_sem['data_gerado'] = str(new_d['data_entrada'])
        df_paletes_sem['data_estoque'] = '-'
        df_paletes_sem['data_consumo'] = '-'
        df_paletes_sem['codigo_tampa_SAP'] = '-'
        df_paletes_sem['numero_palete'] = '-'

        # for para iterar sobre todos os paletes e salvar
        for index, row in df_paletes_sem.iterrows():
            if index < 10:
                index_str = '0' + str(index)
            else:
                index_str = str(index)
            row['documento'] = index_str

        new_d['Paletes'] = df_paletes_sem.to_csv()

        rerun = False
        # Armazena no banco
        try:
            doc_ref = db.collection("Bobina").document(new_d['numero_OT'])
            doc_ref.set(new_d)
            st.success('Bobina adicionada com sucesso!')

            # Limpa cache
            caching.clear_cache()

            # flag para rodar novamente o script
            rerun = True
        except:
            st.error('Falha ao adicionar bobina, tente novamente ou entre em contato com suporte!')

        if rerun:
            st.experimental_rerun()

def adicionar_selante():
    # Formulario para inclusao de selante
    dic = {}

    # Dados dos selantes
    with st.form('forms_selante'):
        dic['status'] = 'Disponível'
        dic['data'] = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
        s1, s2, s3, s4, s5 = st.beta_columns([2, 2, 2, 2, 1])
        dic['numero_lote'] = s1.text_input('Número do lote')
        dic['codigo_SAP'] = s2.text_input('Codigo SAP')
        dic['peso_vedante'] = s3.number_input('Peso do vedante', step=1, format='%i', value=5000)
        dic['lote_interno'] = s4.text_input('Lote interno')
        dic['data_entrada'] = ''
        submitted = s5.form_submit_button('Adicionar selante ao sistema')

    if submitted:

        # Transforma dados do formulário em um dicionário
        keys_values = dic.items()
        new_d = {str(key): str(value) for key, value in keys_values}

        # Verifica campos não preenchidos e os modifica
        for key, value in new_d.items():
            if (value == '') or value == '[]':
                new_d[key] = '-'

        # define a quantidade de paletes gerados pelo selante
        new_d['paletes_gerados'] = int(int(new_d['peso_vedante']) * 2857 / 187200)

        # Define a quantidade de paletes que podem ser gerados pela bobina
        qtd_paletes = int(new_d['paletes_gerados'])

        # cria dataframe e preenche com os dados da bobina
        df_paletes_selante = pd.DataFrame(columns=col_pal_sel, index=list(range(qtd_paletes)))
        df_paletes_selante['numero_lote'] = str(new_d['numero_lote'])
        df_paletes_selante['codigo_SAP'] = str(new_d['codigo_SAP'])
        df_paletes_selante['data_gerado'] = str(new_d['data_entrada'])
        df_paletes_selante['data_estoque'] = '-'
        df_paletes_selante['data_consumo'] = '-'
        df_paletes_selante['lote_semi'] = '-'
        df_paletes_selante['numero_palete'] = '-'

        # for para iterar sobre todos os paletes e salvar
        for index, row in df_paletes_selante.iterrows():
            if index < 10:
                index_str = '0' + str(index)
            else:
                index_str = str(index)
            row['documento'] = index_str

        new_d['Paletes'] = df_paletes_selante.to_csv()

        rerun = False
        # Armazena no banco
        try:
            doc_ref = db.collection("Selante").document(new_d['numero_lote'])
            doc_ref.set(new_d)
            st.success('Bobina adicionada com sucesso!')

            # Limpa cache
            caching.clear_cache()

            # flag para rodar novamente o script
            rerun = True
        except:
            st.error('Falha ao adicionar bobina, tente novamente ou entre em contato com suporte!')

        if rerun:
            st.experimental_rerun()

###########################################################################################################################################
#####                    			cofiguracoes aggrid							                #######
###########################################################################################################################################
def config_grid(height, df, lim_min, lim_max, customizar):
    sample_size = 12
    grid_height = height

    return_mode = 'AS_INPUT'
    return_mode_value = DataReturnMode.__members__[return_mode]
    # return_mode_value = 'AS_INPUT'

    update_mode = 'VALUE_CHANGED'
    update_mode_value = GridUpdateMode.__members__[update_mode]
    # update_mode_value = 'VALUE_CHANGED'

    # enterprise modules
    enable_enterprise_modules = False
    enable_sidebar = False

    # features
    fit_columns_on_grid_load = customizar
    enable_pagination = False
    paginationAutoSize = False
    use_checkbox = False
    enable_selection = False
    selection_mode = 'single'
    rowMultiSelectWithClick = False
    suppressRowDeselection = False

    if use_checkbox:
        groupSelectsChildren = True
        groupSelectsFiltered = True

    # Infer basic colDefs from dataframe types
    gb = GridOptionsBuilder.from_dataframe(df)

    # customize gridOptions
    if not customizar:
        gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc='sum', editable=True)
        gb.configure_column("Medidas", editable=False)
        gb.configure_column('L', editable=False)
        gb.configure_column('V', type=["numericColumn"], precision=5)

        # configures last row to use custom styles based on cell's value, injecting JsCode on components front end
        func_js = """
		function(params) {
		    if (params.value > %f) {
			return {
			    'color': 'black',
			    'backgroundColor': 'orange'
			}
		    } else if(params.value <= %f) {
			return {
			    'color': 'black',
			    'backgroundColor': 'orange'
			}
		    } else if((params.value <= %f) && (params.value >= %f)) {
			return {
			    'color': 'black',
			    'backgroundColor': 'white'
			}
		    } else {
			return {
			    'color': 'black',
			    'backgroundColor': 'red'
			} 
		    } 
		};
		""" % (lim_max, lim_min, lim_max, lim_min)

        cellsytle_jscode = JsCode(func_js)

        gb.configure_column('V', cellStyle=cellsytle_jscode)

    if enable_sidebar:
        gb.configure_side_bar()

    if enable_selection:
        gb.configure_selection(selection_mode)
    if use_checkbox:
        gb.configure_selection(selection_mode, use_checkbox=True, groupSelectsChildren=groupSelectsChildren,
                               groupSelectsFiltered=groupSelectsFiltered)
    if ((selection_mode == 'multiple') & (not use_checkbox)):
        gb.configure_selection(selection_mode, use_checkbox=False, rowMultiSelectWithClick=rowMultiSelectWithClick,
                               suppressRowDeselection=suppressRowDeselection)

    if enable_pagination:
        if paginationAutoSize:
            gb.configure_pagination(paginationAutoPageSize=True)
        else:
            gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=paginationPageSize)

    gb.configure_grid_options(domLayout='normal')
    gridOptions = gb.build()
    return gridOptions, grid_height, return_mode_value, update_mode_value, fit_columns_on_grid_load, enable_enterprise_modules


##########################################################################################################
#####                    			rastreabilidade  		   				                      ########
##########################################################################################################

#################################
# leitura de dados e definicoes #
#################################


# definicao de colunas para leitura d dados do banco
col_bobinas = ['numero_OT', 'data', 'tipo_bobina', 'codigo_bobina', 'peso_bobina', 'codigo_SAP', 'data_entrada',
               'paletes_gerados', 'status']
col_pal_sem = ['numero_OT', 'documento', 'tipo_tampa', 'data_gerado', 'data_estoque', 'data_consumo',
               'codigo_tampa_SAP', 'numero_palete']
col_selante = ['numero_lote', 'lote_interno', 'codigo_SAP', 'peso_vedante', 'data', 'data_entrada', 'paletes_gerados',
               'status']
col_pal_sel = ['numero_lote', 'documento', 'codigo_SAP', 'data_gerado', 'data_estoque', 'data_consumo', 'lote_semi', 'numero_palete']

# leitura e exibicao dos dados das bobinas
df_bobinas, df_pal_sem = load_colecoes('Bobina', col_bobinas, col_pal_sem, 0)
df_selantes, df_pal_com = load_colecoes('Selante', col_selante, col_pal_sel, 1)

# dataframes do fifo sem selante
df_ps_fifo_in = df_pal_sem[(df_pal_sem['data_estoque'] != '-') & (df_pal_sem['data_consumo'] == '-')]
df_ps_fifo_out = df_pal_sem[df_pal_sem['data_consumo'] != '-']

# dataframes do fifo com selante
df_ps_fifo_s_in = df_pal_com[(df_pal_com['data_estoque'] != '-') & (df_pal_com['data_consumo'] == '-')]
df_ps_fifo_s_out = df_pal_com[df_pal_com['data_consumo'] != '-']

#######################
# organizacao da tela #
#######################

# define imagem e barra lateral
col2, imagem, col4 = st.beta_columns([3, 10, 3])
#imagem.write(df_pal_sem)
#imagem.write(df_pal_com)
imagem.image('lid_linha.png')

st.subheader('Inclusao de Bobinas e Selante')

with st.beta_expander('Bobinas'):
    st.subheader('Inserir Bobinas')
    adicionar_bobina()

    st.subheader('Selecionar bobina para uso')
    st1, st2 = st.beta_columns([99, 1])

    st.subheader('Detalhamento das bobinas')
    #st.write(df_bobinas)
    gridOptions, grid_height, return_mode_value, update_mode_value, fit_columns_on_grid_load, enable_enterprise_modules = config_grid(198, df_bobinas, 0, 0, True)
    response = AgGrid(
        df_bobinas,
        gridOptions=gridOptions,
        height=grid_height,
        width='100%',
        data_return_mode=return_mode_value,
        update_mode=update_mode_value,
        fit_columns_on_grid_load=fit_columns_on_grid_load,
        allow_unsafe_jscode=False,  # Set it to True to allow jsfunction to be injected
        enable_enterprise_modules=enable_enterprise_modules)

with st.beta_expander('Selante'):
    st.subheader('Inserir Selante')
    adicionar_selante()

    st.subheader('Selecionar selante para uso')
    st11, st22 = st.beta_columns([99, 1])

    st.subheader('Detalhamento dos selantes')
    #st.write(df_selantes)
    gridOptions, grid_height, return_mode_value, update_mode_value, fit_columns_on_grid_load, enable_enterprise_modules = config_grid(199, df_selantes, 0, 0, True)
    response = AgGrid(
        df_selantes,
        gridOptions=gridOptions,
        height=grid_height,
        width='100%',
        data_return_mode=return_mode_value,
        update_mode=update_mode_value,
        fit_columns_on_grid_load=fit_columns_on_grid_load,
        allow_unsafe_jscode=False,  # Set it to True to allow jsfunction to be injected
        enable_enterprise_modules=enable_enterprise_modules)


st.subheader('Visulizacao do historico de paletes com e sem selante')
with st.beta_expander('Paletes sem selante'):

    gridOptions, grid_height, return_mode_value, update_mode_value, fit_columns_on_grid_load, enable_enterprise_modules = config_grid(400, df_pal_sem, 0, 0, True)
    response = AgGrid(
        df_pal_sem,
        gridOptions=gridOptions,
        height=grid_height,
        width='100%',
        data_return_mode=return_mode_value,
        update_mode=update_mode_value,
        fit_columns_on_grid_load=fit_columns_on_grid_load,
        allow_unsafe_jscode=False,  # Set it to True to allow jsfunction to be injected
        enable_enterprise_modules=enable_enterprise_modules)

with st.beta_expander('Paletes com selante'):

    gridOptions, grid_height, return_mode_value, update_mode_value, fit_columns_on_grid_load, enable_enterprise_modules = config_grid(400, df_pal_com, 0, 0, True)
    response = AgGrid(
        df_pal_com,
        gridOptions=gridOptions,
        height=grid_height,
        width='100%',
        data_return_mode=return_mode_value,
        update_mode=update_mode_value,
        fit_columns_on_grid_load=fit_columns_on_grid_load,
        allow_unsafe_jscode=False,  # Set it to True to allow jsfunction to be injected
        enable_enterprise_modules=enable_enterprise_modules)

###########################################
# Selecionar bobinas disponiveis para uso #
###########################################

# Verifica bobinas disponiveis
df_bobinas_disp = df_bobinas[df_bobinas['status'] == 'Disponível']

# cria selectbox para selecionar bobinas
numero_bobina = st1.selectbox('Selecione a próxima bobina:', list(df_bobinas_disp['numero_OT']))

# botao para teste
st.button('Reset')

# parte do principio que nenhuma bobina foi selecionada
selecionar_bobina = False

# verifica se foi selecionada alguma bobina
if numero_bobina != None:
    selecionar_bobina = st1.button('Utilizar a bobina selecionada?')
else:
    st1.info('Nao ha bobinas disponiveis')

if selecionar_bobina:

    ###################################
    # Coloca anterior como finalizada #
    ###################################

    #verifica se ha bobina em uso
    bobina_em_uso = df_bobinas[df_bobinas['status'] == 'Em uso']
    #st.write(bobina_em_uso)

    if bobina_em_uso.shape[0] > 0:

        # seleciona a bobina em uso
        val_em_uso = bobina_em_uso.iloc[0,0]

        # modifica bobina selecionada para finalizada
        df_bobinas.loc[df_bobinas['numero_OT'] == val_em_uso, 'status'] = 'Finalizada'
        df_bobinas.loc[df_bobinas['numero_OT'] == val_em_uso, 'data_entrada'] = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

        # prepara dados para escrever no banco
        dic_fin = {}
        dic_fin = df_bobinas.loc[df_bobinas['numero_OT'] == val_em_uso].to_dict('records')

        # Transforma dados do formulário em um dicionário
        keys_values = dic_fin[0].items()
        new_fin = {str(key): str(value) for key, value in keys_values}
        documento = new_fin['numero_OT']

        # escreve o dataframe dos paletes na bobina para escrita em banco (nao altera valor, mas escreve para nao perder os dados)
        new_fin['Paletes'] = df_pal_sem[df_pal_sem['numero_OT'] == val_em_uso].to_csv()

        # Armazena no banco as alteracoes na bobina
        try:
            doc_ref = db.collection("Bobina").document(documento)
            doc_ref.set(new_fin)
            st.success('Formulário armazenado com sucesso!')
        except:
            st.error('Falha ao armazenar formulário, tente novamente ou entre em contato com suporte!')
            caching.clear_cache()
    else:
        st.info('Nao havia bobina em uso!')

    ####################################
    # Coloca bobina selecionada em uso #
    ####################################

    # modifica bobina selecionada para uso
    df_bobinas.loc[df_bobinas['numero_OT'] == numero_bobina, 'status'] = 'Em uso'
    df_bobinas.loc[df_bobinas['numero_OT'] == numero_bobina, 'data_entrada'] = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

    # prepara dados para escrever no banco
    dic_bobina_uso = {}
    dic_bobina_uso = df_bobinas.loc[df_bobinas['numero_OT'] == numero_bobina].to_dict('records')

    # Transforma dados do formulário em um dicionário
    keys_values = dic_bobina_uso[0].items()
    new_uso = {str(key): str(value) for key, value in keys_values}
    documento = new_uso['numero_OT']

    # Filtra paletes da bobina em uso e atualiza valores
    df_pal_sem.loc[df_pal_sem['numero_OT'] == numero_bobina, 'data_gerado'] = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
    st.write(df_pal_sem[df_pal_sem['numero_OT'] == numero_bobina])

    st.write(df_pal_sem['numero_palete'])

    # Coloca o numero dos paletes
    if (df_pal_sem['numero_palete'] != '-').any():
        maximo_index = int(df_pal_sem.loc[df_pal_sem['numero_palete'] != '-', 'numero_palete'].max()) + 1
        df_pal_sem.loc[df_pal_sem['numero_OT'] == numero_bobina, 'numero_palete'] = df_pal_sem['documento'] + maximo_index
    else:
        df_pal_sem.loc[df_pal_sem['numero_OT'] == numero_bobina, 'numero_palete'] = df_pal_sem['documento']

    # Escreve o dataframe dos paletes na bobina para escrita em banco
    new_uso['Paletes'] = df_pal_sem[df_pal_sem['numero_OT'] == numero_bobina].to_csv()

    # Flag de rerun da aplicacao
    flag_rerun = False

    # Armazena no banco as alteracoes na bobina
    try:
        doc_ref = db.collection("Bobina").document(documento)
        doc_ref.set(new_uso)
        st.success('Formulário armazenado com sucesso!')
        flag_rerun = True
    except:
        st.error('Falha ao armazenar formulário, tente novamente ou entre em contato com suporte!')
        caching.clear_cache()

    if flag_rerun:
        st.experimental_rerun()

############################
# FIFO paletes sem selante #
############################

# Adiciona paletes
with col2:
    st.subheader('Sem selante')
    col2.write('Ultimos gerados')
    if df_ps_fifo_in.shape[0] < 5:
        add_palete_sem = col2.button('Adicionar palete TP sem Selante')
        if add_palete_sem:

            # verificar bobina em uso
            bobina_atual = df_bobinas[df_bobinas['status'] == 'Em uso']['numero_OT']
            numero_palete = df_pal_sem.loc[(df_pal_sem['numero_OT'] == bobina_atual.iloc[0]) & (df_pal_sem['data_estoque'] == '-'), 'numero_palete'].min()

            df_pal_sem.loc[df_pal_sem['numero_palete'] == numero_palete, 'data_estoque'] = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
            #st.write(df_pal_sem.loc[df_pal_sem['numero_palete'] == numero_palete])

            # prepara dados para escrever no banco
            dic_fifo_in = {}
            dic_fifo_in = df_bobinas.loc[df_bobinas['numero_OT'] == bobina_atual.iloc[0]].to_dict('records')

            # Transforma dados do formulário em um dicionário
            keys_values = dic_fifo_in[0].items()
            new_fifo_in = {str(key): str(value) for key, value in keys_values}
            documento = new_fifo_in['numero_OT']

            # Escreve o dataframe dos paletes na bobina para escrita em banco
            new_fifo_in['Paletes'] = df_pal_sem[df_pal_sem['numero_OT'] == bobina_atual.iloc[0]].to_csv()

            # Flag de rerun da aplicacao
            flag_rerun = False

            # Armazena no banco as alteracoes na bobina
            try:
                doc_ref = db.collection("Bobina").document(documento)
                doc_ref.set(new_fifo_in)
                flag_rerun = True

            except:
                st.error('Falha ao atualizar informacoes do palete, tente novamente ou entre em contato com suporte!')

            if flag_rerun:
                st.experimental_rerun()

    else:
        st.error('Ha paletes demais na reserva')

    fifo_in_show = df_ps_fifo_in.sort_values(by='data_estoque', ascending=True)[['numero_palete', 'tipo_tampa']]
    #st.write(fifo_in_show.head())
    gridOptions, grid_height, return_mode_value, update_mode_value, fit_columns_on_grid_load, enable_enterprise_modules = config_grid(175, fifo_in_show, 0, 0, True)
    response = AgGrid(
        fifo_in_show,
        gridOptions=gridOptions,
        height=grid_height,
        width='100%',
        data_return_mode=return_mode_value,
        update_mode=update_mode_value,
        fit_columns_on_grid_load=fit_columns_on_grid_load,
        allow_unsafe_jscode=False,  # Set it to True to allow jsfunction to be injected
        enable_enterprise_modules=enable_enterprise_modules)

    if fifo_in_show.shape[0] > 0:
        st.info('Proximo palete: ' + str(fifo_in_show.iloc[0, 0]))

# consome paletes

    col2.write('Ultimos consumidos')
    if df_ps_fifo_in.shape[0] > 0:
        con_palete_sem = col2.button('Consumir palete TP sem Selante')
        if con_palete_sem:
            # observa o indice do primeiro elemento do fifo
            numero_palete = df_pal_sem.loc[(df_pal_sem['data_estoque'] != '-') & (df_pal_sem['data_consumo'] == '-'), 'numero_palete'].min()

            # atualiza a data de consumo do palete consumido
            df_pal_sem.loc[(df_pal_sem['numero_palete'] == numero_palete), 'data_consumo'] = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

            #identifica o numero da bobina do palete
            bobina_consumo = df_pal_sem.loc[(df_pal_sem['numero_palete'] == numero_palete), 'numero_OT']

            # prepara dados para escrever no banco
            dic_fifo_out = {}
            dic_fifo_out = df_bobinas.loc[df_bobinas['numero_OT'] == bobina_consumo.iloc[0]].to_dict('records')

            # Transforma dados do formulário em um dicionário
            keys_values = dic_fifo_out[0].items()
            new_fifo_out = {str(key): str(value) for key, value in keys_values}
            documento = new_fifo_out['numero_OT']

            # Escreve o dataframe dos paletes na bobina para escrita em banco
            new_fifo_out['Paletes'] = df_pal_sem[df_pal_sem['numero_OT'] == bobina_consumo.iloc[0]].to_csv()

            # Flag de rerun da aplicacao
            flag_rerun = False

            # Armazena no banco as alteracoes na bobina
            try:
                doc_ref = db.collection("Bobina").document(documento)
                doc_ref.set(new_fifo_out)
                flag_rerun = True

            except:
                st.error('Falha ao atualizar informacoes do palete, tente novamente ou entre em contato com suporte!')

            if flag_rerun:
                st.experimental_rerun()

    else:
        st.error('Nao ha palete sem selante para consumir')

    fifo_out_show = df_ps_fifo_out.sort_values(by='data_consumo', ascending=False)[['numero_palete', 'tipo_tampa']]
    #st.write(fifo_out_show.head())
    gridOptions, grid_height, return_mode_value, update_mode_value, fit_columns_on_grid_load, enable_enterprise_modules = config_grid(175, fifo_out_show, 0, 0, True)
    response = AgGrid(
        fifo_out_show,
        gridOptions=gridOptions,
        height=grid_height,
        width='100%',
        data_return_mode=return_mode_value,
        update_mode=update_mode_value,
        fit_columns_on_grid_load=fit_columns_on_grid_load,
        allow_unsafe_jscode=False,  # Set it to True to allow jsfunction to be injected
        enable_enterprise_modules=enable_enterprise_modules)

###########################################
# Selecionar selantes disponiveis para uso #
###########################################

# Verifica selantes disponiveis
df_selantes_disp = df_selantes[df_selantes['status'] == 'Disponível']

# cria selectbox para selecionar selantes
numero_selante = st11.selectbox('Selecione o próximo selante:', list(df_selantes_disp['numero_lote']))

# parte do principio que nenhuma selante foi selecionada
selecionar_selante = False

# verifica se foi selecionada alguma selante
if numero_selante != None:
    selecionar_selante = st11.button('Utilizar o selante selecionado?')
else:
    st11.info('Nao ha selantes disponiveis')

if selecionar_selante:

    ###################################
    # Coloca anterior como finalizada #
    ###################################

    #verifica se ha selante em uso
    selante_em_uso = df_selantes[df_selantes['status'] == 'Em uso']
    #st.write(selante_em_uso)

    if selante_em_uso.shape[0] > 0:

        # seleciona a selante em uso
        val_em_uso = selante_em_uso.iloc[0,0]

        # modifica selante selecionada para finalizada
        df_selantes.loc[df_selantes['numero_lote'] == val_em_uso, 'status'] = 'Finalizada'
        df_selantes.loc[df_selantes['numero_lote'] == val_em_uso, 'data_entrada'] = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

        # prepara dados para escrever no banco
        dic_fin = {}
        dic_fin = df_selantes.loc[df_selantes['numero_lote'] == val_em_uso].to_dict('records')

        # Transforma dados do formulário em um dicionário
        keys_values = dic_fin[0].items()
        new_fin = {str(key): str(value) for key, value in keys_values}
        documento = new_fin['numero_lote']

        # escreve o dataframe dos paletes na selante para escrita em banco (nao altera valor, mas escreve para nao perder os dados)
        new_fin['Paletes'] = df_pal_com[df_pal_com['numero_lote'] == val_em_uso].to_csv()

        # Armazena no banco as alteracoes na selante
        try:
            doc_ref = db.collection("Selante").document(documento)
            doc_ref.set(new_fin)
            st.success('Formulário armazenado com sucesso!')
        except:
            st.error('Falha ao armazenar formulário, tente novamente ou entre em contato com suporte!')
            caching.clear_cache()
    else:
        st.info('Nao havia selante em uso!')

    ####################################
    # Coloca selante selecionada em uso #
    ####################################

    # modifica selante selecionada para uso
    df_selantes.loc[df_selantes['numero_lote'] == numero_selante, 'status'] = 'Em uso'
    df_selantes.loc[df_selantes['numero_lote'] == numero_selante, 'data_entrada'] = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

    # prepara dados para escrever no banco
    dic_selante_uso = {}
    dic_selante_uso = df_selantes.loc[df_selantes['numero_lote'] == numero_selante].to_dict('records')

    # Transforma dados do formulário em um dicionário
    keys_values = dic_selante_uso[0].items()
    new_uso = {str(key): str(value) for key, value in keys_values}
    documento = new_uso['numero_lote']

    # Filtra paletes da selante em uso e atualiza valores
    df_pal_com.loc[df_pal_com['numero_lote'] == numero_selante, 'data_gerado'] = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
    st.write(df_pal_com[df_pal_com['numero_lote'] == numero_selante])

    st.write(df_pal_com['numero_palete'])

    # Coloca o numero dos paletes
    if (df_pal_com['numero_palete'] != '-').any():
        maximo_index = int(df_pal_com.loc[df_pal_com['numero_palete'] != '-', 'numero_palete'].max()) + 1
        df_pal_com.loc[df_pal_com['numero_lote'] == numero_selante, 'numero_palete'] = df_pal_com['documento'] + maximo_index
    else:
        df_pal_com.loc[df_pal_com['numero_lote'] == numero_selante, 'numero_palete'] = df_pal_com['documento']

    # Escreve o dataframe dos paletes na selante para escrita em banco
    new_uso['Paletes'] = df_pal_com[df_pal_com['numero_lote'] == numero_selante].to_csv()

    # Flag de rerun da aplicacao
    flag_rerun = False

    # Armazena no banco as alteracoes na selante
    try:
        doc_ref = db.collection("Selante").document(documento)
        doc_ref.set(new_uso)
        st.success('Formulário armazenado com sucesso!')
        flag_rerun = True
    except:
        st.error('Falha ao armazenar formulário, tente novamente ou entre em contato com suporte!')
        caching.clear_cache()

    if flag_rerun:
        st.experimental_rerun()

############################
# fifo_s paletes sem selante #
############################

# Adiciona paletes
with col4:
    st.subheader('Sem selante')
    col4.write('Ultimos gerados')
    if df_ps_fifo_s_in.shape[0] < 5:
        add_palete_sem = col4.button('Adicionar palete TP com Selante')
        if add_palete_sem:

            # verificar selante em uso
            selante_atual = df_selantes[df_selantes['status'] == 'Em uso']['numero_lote']
            numero_palete = df_pal_com.loc[(df_pal_com['numero_lote'] == selante_atual.iloc[0]) & (df_pal_com['data_estoque'] == '-'), 'numero_palete'].min()

            df_pal_com.loc[df_pal_com['numero_palete'] == numero_palete, 'data_estoque'] = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
            #st.write(df_pal_com.loc[df_pal_com['numero_palete'] == numero_palete])

            # prepara dados para escrever no banco
            dic_fifo_s_in = {}
            dic_fifo_s_in = df_selantes.loc[df_selantes['numero_lote'] == selante_atual.iloc[0]].to_dict('records')

            # Transforma dados do formulário em um dicionário
            keys_values = dic_fifo_s_in[0].items()
            new_fifo_s_in = {str(key): str(value) for key, value in keys_values}
            documento = new_fifo_s_in['numero_lote']

            # Escreve o dataframe dos paletes na selante para escrita em banco
            new_fifo_s_in['Paletes'] = df_pal_com[df_pal_com['numero_lote'] == selante_atual.iloc[0]].to_csv()

            # Flag de rerun da aplicacao
            flag_rerun = False

            # Armazena no banco as alteracoes na selante
            try:
                doc_ref = db.collection("Selante").document(documento)
                doc_ref.set(new_fifo_s_in)
                flag_rerun = True

            except:
                st.error('Falha ao atualizar informacoes do palete, tente novamente ou entre em contato com suporte!')

            if flag_rerun:
                st.experimental_rerun()

    else:
        st.error('Ha paletes demais na reserva')

    fifo_s_in_show = df_ps_fifo_s_in.sort_values(by='data_estoque', ascending=True)[['numero_palete', 'codigo_SAP']]
    #st.write(fifo_s_in_show.head())

    gridOptions, grid_height, return_mode_value, update_mode_value, fit_columns_on_grid_load, enable_enterprise_modules = config_grid(175, fifo_s_in_show, 0, 0, True)
    response = AgGrid(
        fifo_s_in_show,
        gridOptions=gridOptions,
        height=grid_height,
        width='100%',
        data_return_mode=return_mode_value,
        update_mode=update_mode_value,
        fit_columns_on_grid_load=fit_columns_on_grid_load,
        allow_unsafe_jscode=False,  # Set it to True to allow jsfunction to be injected
        enable_enterprise_modules=enable_enterprise_modules)

    if fifo_s_in_show.shape[0] > 0:
        st.success('Proximo palete: ' + str(fifo_s_in_show.iloc[0, 0]))

# consome paletes

    col4.write('Ultimos consumidos')
    if df_ps_fifo_s_in.shape[0] > 0:
        con_palete_sem = col4.button('Consumir palete TP com Selante')
        if con_palete_sem:
            # observa o indice do primeiro elemento do fifo_s
            numero_palete = df_pal_com.loc[(df_pal_com['data_estoque'] != '-') & (df_pal_com['data_consumo'] == '-'), 'numero_palete'].min()

            # atualiza a data de consumo do palete consumido
            df_pal_com.loc[(df_pal_com['numero_palete'] == numero_palete), 'data_consumo'] = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

            #identifica o numero da selante do palete
            selante_consumo = df_pal_com.loc[(df_pal_com['numero_palete'] == numero_palete), 'numero_lote']

            # prepara dados para escrever no banco
            dic_fifo_s_out = {}
            dic_fifo_s_out = df_selantes.loc[df_selantes['numero_lote'] == selante_consumo.iloc[0]].to_dict('records')

            # Transforma dados do formulário em um dicionário
            keys_values = dic_fifo_s_out[0].items()
            new_fifo_s_out = {str(key): str(value) for key, value in keys_values}
            documento = new_fifo_s_out['numero_lote']

            # Escreve o dataframe dos paletes na selante para escrita em banco
            new_fifo_s_out['Paletes'] = df_pal_com[df_pal_com['numero_lote'] == selante_consumo.iloc[0]].to_csv()

            # Flag de rerun da aplicacao
            flag_rerun = False

            # Armazena no banco as alteracoes na selante
            try:
                doc_ref = db.collection("Selante").document(documento)
                doc_ref.set(new_fifo_s_out)
                flag_rerun = True

            except:
                st.error('Falha ao atualizar informacoes do palete, tente novamente ou entre em contato com suporte!')

            if flag_rerun:
                st.experimental_rerun()

    else:
        st.error('Nao ha palete sem selante para consumir')

    fifo_s_out_show = df_ps_fifo_s_out.sort_values(by='data_consumo', ascending=False)[['numero_palete', 'codigo_SAP']]
    #st.write(fifo_s_out_show.head())

    gridOptions, grid_height, return_mode_value, update_mode_value, fit_columns_on_grid_load, enable_enterprise_modules = config_grid(175, fifo_s_out_show, 0, 0, True)
    response = AgGrid(
        fifo_s_out_show,
        gridOptions=gridOptions,
        height=grid_height,
        width='100%',
        data_return_mode=return_mode_value,
        update_mode=update_mode_value,
        fit_columns_on_grid_load=fit_columns_on_grid_load,
        allow_unsafe_jscode=False,  # Set it to True to allow jsfunction to be injected
        enable_enterprise_modules=enable_enterprise_modules)

