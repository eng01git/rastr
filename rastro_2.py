import streamlit as st
from streamlit import caching
import pandas as pd
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
textkey_2 = """{\n  \"type\": \"service_account\",\n  \"project_id\": \"lid-forms\",\n  \"private_key_id\": \"de4fcc45d24308eaa9101b4d4d651c0e1f1c192e\",\n  \"private_key\": \"-----BEGIN PRIVATE KEY-----\\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCQL7wXeUw7bxgB\\n0kivlcQyVhrBW+ufV1cgv1ySMjqhBxuGK6/4x3Po2/a/phcPxYN7hfsmcq1ZmCMx\\nMHU2TicbRtxA0XqXCi1wfbHYUQk49fT7SJRI9R5C3cCq6hicAYXAdC0BCqvXcmB7\\n8JSRBhdiLmMziQlcb1OkKtTrMkg8/2xhPXVQ8snBzYxrcpGL70IUMW/4FKdABBxg\\ne1uV8Xs11e3pWqQVNxd6FKnanBg/88/wleMb0wZRc0ULhrVEJCFYX8ycjLgoMn4+\\nKNDXdl7zs41IoEdSqs9VTjrrJFGPE6lxUO/qb4FE76qU/4BEmyXjiggLFpu+mjOO\\n0JvN2E6xAgMBAAECggEAB0NISQcUoR0doKCG2xqtqSVvhT7hQFj7bAxc7YZMhWZL\\na3eRjnP+3C4RoKINS6o/eb42zOnTiThMdC1Z3MmUrF87jU5KoQdjtjoL9nalLXKC\\nNmgiWVxze5saRIxfKfiPqVvmFRqEVmljVSA6COYS0SC/YXitI96oYBQXk939XTPN\\nz5LxXyubM00vK1MgdCw8lMajE0l1w7FkqyupolStYeX8l23Kfp6o/Kte/IdZpWR6\\ngefnMEvVCUorNjpuFlvOQrxgm6ygAsuFglRshPqXzUS9761TyBcKPdr4znAA3gns\\nrEqi+6Lrh9xz+t5K8aHodjzvNHQ9yjAiGZHZsoO5WQKBgQDK7IXXslOz7lJ5ZLSl\\njJRtLbs6C0cOmmf+7UQXJmtsL0OHsYgWMzTtrqEo2EqCq0C8UCvCCyUs/d0LrwU4\\n40U9+CUYQMP9PtezqK23XFuLg7upJzY2AH3mNkRr8CMCuyWisw+W/o8QF6jUijtP\\nT0JIrdYyfrGUEx+JnogW4pW+pQKBgQC15j3D/0zRBaM71DjXGc9UDX2M7V56e07S\\nsEJvvzTPbh86VQ3sZTVPoC1jXhV/IzyT3+uxMvrNhEwP15pQzLkMW2J/uZzI3Q+L\\nvhUl6Lk8RIMTFFO2CkNfugPZwPmUxe9/Cu0y9AbeBR7v1zouxFkaNAEkMOrpQ3Ds\\nDwWqLbL+HQKBgAlzMlh1KYi7lIOquO7suQzMkGeHluuLLUSl8AHT/DSxjseG8Pt3\\nrwNSmpa4W9/x8bXTVfZXZofN2rlskSWxD8xu/es/OOFWR91KAa0EVA8PN3INLW0e\\nYL6T0GPmbvr1lC8bf6JcgHUTZP1g4poy6rdPwSXg2Iw4x8M06smGC8sxAoGBAKAx\\nKGwXxhq+kEb8WyJ0BHbNeqhF01KijYRW3etzxJp5LN8+UIjDiPOa6N392YiiC5Nf\\nPD5N2zprLGE3Sxulb8JGKLS7TixHIo261P0RuzAsVhLTb/V9jGAdfY6juCkhOA32\\nHXcmGXYlpF0senz9RkshSXAJ9JeBYU1C3YZFwMCxAoGAaFm980daY3c3P/6mSWC6\\nTImniGbAUbUNFxpC3VUcDTtaC4WtGNe5vcVbvPxWXqBTPo8S7q5eq0JWJipfy4Gp\\ncU3+qMM+Z9jLwasmwKAjN066BH1gPC6AB9m+T2U/N6EY1mTp+DEYfFGhwJCB9coC\\nJ2krpcK4f+zsV7XGgnwUhic=\\n-----END PRIVATE KEY-----\\n\",\n  \"client_email\": \"firebase-adminsdk-r4dlw@lid-forms.iam.gserviceaccount.com\",\n  \"client_id\": \"101767194762733526952\",\n  \"auth_uri\": \"https://accounts.google.com/o/oauth2/auth\",\n  \"token_uri\": \"https://oauth2.googleapis.com/token\",\n  \"auth_provider_x509_cert_url\": \"https://www.googleapis.com/oauth2/v1/certs\",\n  \"client_x509_cert_url\": \"https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-r4dlw%40lid-forms.iam.gserviceaccount.com\"\n}\n"""

# Pega as configurações do banco do segredo
key_dict = json.loads(textkey_2)
creds = service_account.Credentials.from_service_account_info(key_dict)

# Seleciona o projeto
db = firestore.Client(credentials=creds, project="lid-forms")

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
@st.cache(suppress_st_warning=True)
def load_colecoes(colecao, colunas, tipo):
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
        index += 1
    # Transforma o dicionario em dataframe
    df = pd.DataFrame.from_dict(dicionario)

    # troca linhas com colunas
    df = df.T

    if tipo == 0:  # Bobinas
        # Transforma string em tipo data
        df['data'] = pd.to_datetime(df['data'])

        # Ordena os dados pela data
        df = df.sort_values(by=['data'], ascending=False)

        # Remove o index
        df = df.reset_index(drop=True)

        # Ordena as colunas
        df = df[colunas]

    if tipo == 1:  # paletes sem selante
        # Transforma string em tipo data

        df['data_gerado'] = pd.to_datetime(df['data_gerado'])

        # avaliar as demais datas posteriormente, filtro? string serve?

        # ordena os dados
        df = df.sort_values(by=['data_gerado', 'documento'], ascending=[True, True])
        df = df.reset_index(drop=True)

        # Ordena as colunas
        df = df[colunas]

        # adiciona o index
        df['numero_palete'] = df.index

    return df


def adicionar_bobina():
    # Formulario para inclusao de bobinas
    dic = {}

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
        # Limpa cache
        caching.clear_cache()
        # Transforma dados do formulário em um dicionário
        keys_values = dic.items()
        new_d = {str(key): str(value) for key, value in keys_values}

        # Verifica campos não preenchidos e os modifica
        for key, value in new_d.items():
            if (value == '') or value == '[]':
                new_d[key] = '-'

        # define a quantidade de paletes gerados pela bobina
        new_d['paletes_gerados'] = int(int(new_d['peso_bobina']) * 412 / 187200)

        # Armazena no banco
        try:
            doc_ref = db.collection("Bobina").document(new_d['numero_OT'])
            doc_ref.set(new_d)
            st.success('Bobina adicionada com sucesso!')
        except:
            st.error('Falha ao adicionar bobina, tente novamente ou entre em contato com suporte!')
        st.experimental_rerun()

def adicionar_selante():
    # Formulario para inclusao de bobinas
    dic = {}

    with st.form('forms_Selante'):
        dic['status'] = 'Disponível'
        dic['data'] = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
        s1, s2, s3, s4, s5 = st.beta_columns([2, 2, 2, 2, 1])
        dic['numero_lote'] = s1.text_input('Número do lote')
        dic['codigo_SAP'] = s2.text_input('Codigo SAP')
        dic['peso_vedante'] = s3.number_input('Peso do vedante', step=1, format='%i', value=9000)
        dic['lote_interno'] = s4.text_input('Lote interno')
        dic['data_entrada'] = ''
        submitted = s5.form_submit_button('Adicionar vedante ao sistema')

    if submitted:
        # Limpa cache
        caching.clear_cache()
        # Transforma dados do formulário em um dicionário
        keys_values = dic.items()
        new_d = {str(key): str(value) for key, value in keys_values}

        # Verifica campos não preenchidos e os modifica
        for key, value in new_d.items():
            if (value == '') or value == '[]':
                new_d[key] = '-'

        # define a quantidade de paletes gerados pela bobina
        new_d['paletes_gerados'] = int(int(new_d['peso_vedante']) * 2857 / 187200)

        # Armazena no banco
        try:
            doc_ref = db.collection("Selante").document(new_d['numero_lote'])
            doc_ref.set(new_d)
            st.success('Selante adicionado com sucesso!')
        except:
            st.error('Falha ao adicionar selante, tente novamente ou entre em contato com suporte!')
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
               'codigo_tampa_SAP']
col_selante = ['numero_lote', 'lote_interno', 'codigo_SAP', 'peso_vedante', 'data', 'data_entrada', 'paletes_gerados',
               'status']
col_pal_selante = ['numero_lote', 'documento', 'codigo_SAP', 'data_gerado', 'data_estoque', 'data_consumo', 'lote_semi']

# leitura e exibicao dos dados das bobinas
df_bobinas = load_colecoes('Bobina', col_bobinas, 0)
df_pal_sem = load_colecoes('B_palete', col_pal_sem, 1)
df_selantes = load_colecoes('Selante', col_selante, 0)
df_pal_selante = load_colecoes('S_palete', col_pal_selante, 1)

# dataframes do fifo sem selante
df_ps_fifo_in = df_pal_sem[(df_pal_sem['data_estoque'] != '-') & (df_pal_sem['data_consumo'] == '-')]
df_ps_fifo_out = df_pal_sem[df_pal_sem['data_consumo'] != '-']

# dataframes do fifo com selante
df_selante_fifo_in = df_pal_selante[(df_pal_selante['data_estoque'] != '-') & (df_pal_selante['data_consumo'] == '-')]
df_selante_fifo_out = df_pal_selante[df_pal_selante['data_consumo'] != '-']

#######################
# organizacao da tela #
#######################

# define imagem e barra lateral
col2, imagem, col4 = st.beta_columns([3, 10, 3])

imagem.image('lid_linha.png')

st.subheader('Inclusao de Bobinas e Selante')

with st.beta_expander('Bobinas'):
    st.subheader('Inserir Bobinas')
    adicionar_bobina()

    st.subheader('Selecionar bobina para uso')
    st1, st2 = st.beta_columns([99, 1])

    st.subheader('Detalhamento das bobinas')
    st.write(df_bobinas)

with st.beta_expander('Selante'):
    st.subheader('Inserir Selante')
    adicionar_selante()

    st.subheader('Selecionar selante para uso')
    st11, st22 = st.beta_columns([99, 1])

    st.subheader('Detalhamento dos selantes')
    st.write(df_selantes)

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

    bobina_em_uso = df_bobinas[df_bobinas['status'] == 'Em uso']
    st.write(bobina_em_uso)
    if bobina_em_uso.shape[0] > 0:
        bobina_em_uso['status'] = 'Finalizada'
        dic_fin = {}
        dic_fin = bobina_em_uso.to_dict('records')

        # Limpa cache
        caching.clear_cache()

        # Transforma dados do formulário em um dicionário
        keys_values = dic_fin[0].items()
        new_fin = {str(key): str(value) for key, value in keys_values}
        documento = new_fin['numero_OT']

        # Armazena no banco as alteracoes na bobina
        try:
            doc_ref = db.collection("Bobina").document(documento)
            doc_ref.set(new_fin)
            st.success('Formulário armazenado com sucesso!')
        except:
            st.error('Falha ao armazenar formulário, tente novamente ou entre em contato com suporte!')
    else:
        st.info('Nao havia bobina em uso!')

    ####################################
    # Coloca bobina selecionada em uso #
    ####################################

    row_uso = df_bobinas_disp.loc[df_bobinas_disp['numero_OT'] == numero_bobina]
    row_uso['status'] = 'Em uso'
    row_uso['data_entrada'] = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
    dic_uso = {}
    dic_uso = row_uso.to_dict('records')

    # Limpa cache
    caching.clear_cache()

    # Transforma dados do formulário em um dicionário
    keys_values = dic_uso[0].items()
    new_uso = {str(key): str(value) for key, value in keys_values}
    documento = new_uso['numero_OT']

    # Armazena no banco as alteracoes na bobina
    try:
        doc_ref = db.collection("Bobina").document(documento)
        doc_ref.set(new_uso)
        st.success('Formulário armazenado com sucesso!')
    except:
        st.error('Falha ao armazenar formulário, tente novamente ou entre em contato com suporte!')

    #############################################
    # Cria os paletes relativos a bobina em uso #
    #############################################

    # Define a quantidade de paletes que podem ser gerados pela bobina
    qtd_paletes = int(new_uso['paletes_gerados'])

    # cria dataframe e preenche com os dados da bobina
    df_paletes_sem = pd.DataFrame(columns=col_pal_sem, index=list(range(qtd_paletes)))
    df_paletes_sem['numero_OT'] = str(new_uso['numero_OT'])
    df_paletes_sem['tipo_tampa'] = str(new_uso['tipo_bobina'])
    df_paletes_sem['data_gerado'] = str(new_uso['data_entrada'])
    df_paletes_sem['data_estoque'] = '-'
    df_paletes_sem['data_consumo'] = '-'
    df_paletes_sem['codigo_tampa_SAP'] = '-'

    # Armazena no banco os paletes gerados
    batch = db.batch()

    # for para iterar sobre todos os paletes e salvar
    for index, row in df_paletes_sem.iterrows():
        if index < 10:
            index_str = '0' + str(index)
        else:
            index_str = str(index)

        documento = str(row['numero_OT']) + '_' + index_str
        ref = db.collection('B_palete').document(documento)
        row_string = row.astype(str)
        batch.set(ref, row_string.to_dict())
    try:
        # Limpa cache
        caching.clear_cache()

        # escreve no banco
        batch.commit()
    except:
        st.error('Falha ao armazenar formulário, tente novamente ou entre em contato com suporte!')
    st.experimental_rerun()

############################
# FIFO paletes sem selante #
############################
with col2:
    st.subheader('Sem selante')
    col2.write('Ultimos gerados')
    if df_ps_fifo_in.shape[0] < 5:
        add_palete_sem = col2.button('Adicionar palete TP sem Selante')
        if add_palete_sem:

            # verificar bobina em uso
            bobina_atual = df_bobinas[df_bobinas['status'] == 'Em uso']['numero_OT']

            # filtra a bobina atual e valores em data_estoque preenchidos
            aux_pal_sem = df_pal_sem[
                (df_pal_sem['numero_OT'] == bobina_atual.iloc[0]) & (df_pal_sem['data_estoque'] == '-')]

            # define o proximo palete a ser inserido no fifo
            palete_info = df_pal_sem.iloc[int(aux_pal_sem.iloc[0, 7])]

            # salva o documento a ser modificado
            documento = palete_info['documento']

            # define as colunas que serao escritas
            palete_info = palete_info[
                ['numero_OT', 'tipo_tampa', 'data_gerado', 'data_estoque', 'data_consumo', 'codigo_tampa_SAP']]

            # altera o valor data_estoque para a data e hora atual
            palete_info['data_estoque'] = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
            # st.write(palete_info.to_dict())

            # Transforma dados do formulário em um dicionário
            keys_values = palete_info.items()
            update_palete = {str(key): str(value) for key, value in keys_values}

            # Armazena no banco as alteracoes na bobina
            try:
                doc_ref = db.collection("B_palete").document(documento)
                doc_ref.set(update_palete)
                # st.success('Palete atualizado com sucesso!')

                # Limpa cache
                caching.clear_cache()

            except:
                st.error('Falha ao atualizar informacoes do palete, tente novamente ou entre em contato com suporte!')
            st.experimental_rerun()
    else:
        st.error('Ha paletes demais sem selante na reserva')

    fifo_in_show = df_ps_fifo_in.sort_values(by='data_estoque', ascending=True)[['numero_palete', 'tipo_tampa']]
    st.write(fifo_in_show.head())

    if fifo_in_show.shape[0] > 0:
        st.info('Proximo palete a ser consumido: ' + str(fifo_in_show.iloc[0, 0]))

    col2.write('Ultimos consumidos')
    if df_ps_fifo_in.shape[0] > 0:
        con_palete_sem = col2.button('Consumir palete TP sem Selante')
        if con_palete_sem:
            # observa o indice do primeiro elemento do fifo
            palete_info = df_pal_sem.iloc[df_ps_fifo_in.iloc[0, 7]]

            # salva o documento a ser modificado
            documento = palete_info['documento']

            # define as colunas que serao escritas
            palete_info = palete_info[
                ['numero_OT', 'tipo_tampa', 'data_gerado', 'data_estoque', 'data_consumo', 'codigo_tampa_SAP']]

            # altera o valor data_estoque para a data e hora atual
            palete_info['data_consumo'] = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
            # st.write(palete_info.to_dict())

            # Transforma dados do formulário em um dicionário
            keys_values = palete_info.items()
            update_palete = {str(key): str(value) for key, value in keys_values}

            # Armazena no banco as alteracoes na bobina
            try:
                doc_ref = db.collection("B_palete").document(documento)
                doc_ref.set(update_palete)
                # st.success('Palete atualizado com sucesso!')

                # Limpa cache
                caching.clear_cache()
            except:
                st.error('Falha ao atualizar informacoes do palete, tente novamente ou entre em contato com suporte!')
            st.experimental_rerun()
    else:
        st.error('Nao ha palete sem selante para consumir')

    fifo_out_show = df_ps_fifo_out.sort_values(by='data_consumo', ascending=False)[['numero_palete', 'tipo_tampa']]
    st.write(fifo_out_show.head())

############################################
# Selecionar selantes disponiveis para uso #
############################################

# Verifica selantes disponiveis
df_selantes_disp = df_selantes[df_selantes['status'] == 'Disponível']

# cria selectbox para selecionar selantes
numero_selante = st11.selectbox('Selecione o próximo selante:', list(df_selantes_disp['numero_lote']))

# parte do principio que nenhuma selante foi selecionada
selecionar_selante = False

# verifica se foi selecionada alguma selante
if numero_selante != None:
    selecionar_selante = st11.button('Utilizar a selante selecionado?')
else:
    st11.info('Nao ha selantes disponiveis')

if selecionar_selante:

    ###################################
    # Coloca anterior como finalizada #
    ###################################

    selante_em_uso = df_selantes[df_selantes['status'] == 'Em uso']
    st.write(selante_em_uso)
    if selante_em_uso.shape[0] > 0:
        selante_em_uso['status'] = 'Finalizada'
        dic__fin = {}
        dic__fin = selante_em_uso.to_dict('records')

        # Limpa cache
        caching.clear_cache()

        # Transforma dados do formulário em um dicionário
        keys_values = dic__fin[0].items()
        new_fin = {str(key): str(value) for key, value in keys_values}
        documento = new_fin['numero_lote']

        # Armazena no banco as alteracoes na selante
        try:
            doc_ref = db.collection("Selante").document(documento)
            doc_ref.set(new_fin)
            st.success('Formulário armazenado com sucesso!')
        except:
            st.error('Falha ao armazenar formulário, tente novamente ou entre em contato com suporte!')
    else:
        st.info('Nao havia selante em uso!')

    ####################################
    # Coloca selante selecionada em uso #
    ####################################

    row_uso = df_selantes_disp.loc[df_selantes_disp['numero_lote'] == numero_selante]
    row_uso['status'] = 'Em uso'
    row_uso['data_entrada'] = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
    dic__uso = {}
    dic__uso = row_uso.to_dict('records')

    # Limpa cache
    caching.clear_cache()

    # Transforma dados do formulário em um dicionário
    keys_values = dic__uso[0].items()
    new__uso = {str(key): str(value) for key, value in keys_values}
    documento = new__uso['numero_lote']

    # Armazena no banco as alteracoes na selante
    try:
        doc_ref = db.collection("Selante").document(documento)
        doc_ref.set(new__uso)
        st.success('Formulário armazenado com sucesso!')
    except:
        st.error('Falha ao armazenar formulário, tente novamente ou entre em contato com suporte!')

    #############################################
    # Cria os paletes relativos a selante em uso #
    #############################################

    # Define a quantidade de paletes que podem ser gerados pela selante
    qtd_paletes = int(new__uso['paletes_gerados'])

    # cria dataframe e preenche com os dados da selante
    df_paletes_selante = pd.DataFrame(columns=col_pal_selante, index=list(range(qtd_paletes)))
    df_paletes_selante['numero_lote'] = str(new__uso['numero_lote'])
    df_paletes_selante['codigo_SAP'] = str(new__uso['codigo_SAP'])
    df_paletes_selante['data_gerado'] = str(new__uso['data_entrada'])
    df_paletes_selante['data_estoque'] = '-'
    df_paletes_selante['data_consumo'] = '-'
    df_paletes_selante['lote_semi'] = '-'

    # Armazena no banco os paletes gerados
    batch = db.batch()

    # for para iterar sobre todos os paletes e salvar
    for index, row in df_paletes_selante.iterrows():
        if index < 10:
            index_str = '0' + str(index)
        else:
            index_str = str(index)

        documento = str(row['numero_lote']) + '_' + index_str
        ref = db.collection('S_palete').document(documento)
        row_string = row.astype(str)
        batch.set(ref, row_string.to_dict())
    try:
        # Limpa cache
        caching.clear_cache()

        # escreve no banco
        batch.commit()
    except:
        st.error('Falha ao armazenar formulário, tente novamente ou entre em contato com suporte!')
    st.experimental_rerun()
    
############################
# FIFO selantes com selante #
############################
with col4:
    st.subheader('Com selante')
    col4.write('Ultimos gerados')
    if df_selante_fifo_in.shape[0] < 5:
        add_palete_com = col4.button('Adicionar palete TP com Selante')
        if add_palete_com:

            # verificar selante em uso
            selante_atual = df_selantes[df_selantes['status'] == 'Em uso']['numero_lote']

            # filtra a selante atual e valores em data_estoque preenchidos
            aux_pal_com = df_pal_selante[
                (df_pal_selante['numero_lote'] == selante_atual.iloc[0]) & (df_pal_selante['data_estoque'] == '-')]

            # define o proximo palete a ser inserido no fifo
            palete__info = df_pal_selante.iloc[int(aux_pal_com.iloc[0, 7])]

            # salva o documento a ser modificado
            documento = palete__info['documento']

            # define as colunas que serao escritas
            palete__info = palete__info[['numero_lote', 'codigo_SAP', 'data_gerado', 'data_estoque', 'data_consumo', ]]

            # altera o valor data_estoque para a data e hora atual
            palete__info['data_estoque'] = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
            # st.write(palete__info.to_dict())

            # Transforma dados do formulário em um dicionário
            keys_values = palete__info.items()
            update_palete = {str(key): str(value) for key, value in keys_values}

            # Armazena no banco as alteracoes na selante
            try:
                doc_ref = db.collection("S_palete").document(documento)
                doc_ref.set(update_palete)
                # st.success('Palete atualizado com sucesso!')

                # Limpa cache
                caching.clear_cache()
            except:
                st.error('Falha ao atualizar informcoes do palete, tente novamente ou entre em contato com suporte!')
            st.experimental_rerun()

    else:
        st.error('Ha selantes demais com selante na reserva')

    fifo_in_show2 = df_selante_fifo_in.sort_values(by='data_estoque', ascending=True)[['numero_palete', 'codigo_SAP']]
    st.write(fifo_in_show2.head())

    if fifo_in_show2.shape[0] > 0:
        st.success('Proximo palete a ser consumido: ' + str(fifo_in_show2.iloc[0, 0]))

    col4.write('Ultimos consumidos')
    if df_selante_fifo_in.shape[0] > 0:
        con_palete_com = col4.button('Consumir palete TP com Selante')
        if con_palete_com:
            # observa o indice do primeiro elemento do fifo
            palete__info = df_pal_selante.iloc[df_selante_fifo_in.iloc[0, 7]]

            # salva o documento a ser modificado
            documento = palete__info['documento']

            # define as colunas que serao escritas
            palete__info = palete__info[['numero_lote', 'codigo_SAP', 'data_gerado', 'data_estoque', 'data_consumo', ]]

            # altera o valor data_estoque para a data e hora atual
            palete__info['data_consumo'] = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
            # st.write(palete__info.to_dict())

            # Transforma dados do formulário em um dicionário
            keys_values = palete__info.items()
            update_palete = {str(key): str(value) for key, value in keys_values}

            # Armazena no banco as alteracoes na selante
            try:
                doc_ref = db.collection("S_palete").document(documento)
                doc_ref.set(update_palete)
                # st.success('Palete atualizado com sucesso!')

                # Limpa cache
                caching.clear_cache()
            except:
                st.error('Falha ao atualizar informacoes do palete, tente novamente ou entre em contato com suporte!')
            st.experimental_rerun()
    else:
        st.error('Nao ha palete com selante para consumir')

    fifo_out_show2 = df_selante_fifo_out.sort_values(by='data_consumo', ascending=False)[['numero_palete', 'codigo_SAP']]
    st.write(fifo_out_show2.head())
