import streamlit as st
from streamlit import caching
import pandas as pd
import numpy as np
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, JsCode
import streamlit.components.v1 as components
import base64
import json
from datetime import date, datetime, time
import pytz
from io import StringIO

from google.cloud import firestore
from google.oauth2 import service_account

######################################################################################################
# Configurações da página
######################################################################################################

st.set_page_config(
	page_title="Cordax",
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
#####								funcoes																			#########
###########################################################################################################################################

# Define cores para os valores validos ou invalidos
def color(val):
	if val == 'invalido':
		color = 'red'
	else:
		color = 'white'
	return 'background-color: %s' % color


def adicionar_ferramental(df_ferramenta, nomes, colecao):

	# seleção do modo de inclusão
	modo = st.radio('Modo de inclusão', ['Manual', 'Planilha'])

	# inclusão manual
	if modo == 'Manual':
		with st.form('adicionar ferramental'):
			# layout
			include = {}

			include['Data'] = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
			include['ID'] = st.text_input('Identificação da ferramenta')
			include['Nome'] = st.selectbox('Colaborador', nomes)
			include['Status'] = 'Disponível'
			include['Conjunto'] = '-'
			include['Reformada'] = 'Não'

			ferramentas = df_ferramenta.drop(['Data', 'ID', 'Nome', 'Status', 'Conjunto', 'Reformada'], axis=1)

			for col in ferramentas.columns:
				include[col] = st.number_input('Valor da medida ' + col + ':', step=0.0001, format="%0.1111f")

			submitted = st.form_submit_button('Adicionar ferramenta')

			if submitted:

				# define o nome do documento
				documento = include['ID']

				if not df_ferramenta[df_ferramenta['ID'] == documento].shape[0] > 0:
					# Adiciona os valores ao dataframe inputado
					df_ferramenta = df_ferramenta.append(include, ignore_index=True)

					# flag para rodar novamente o script
					rerun = False

					# Armazena no banco
					try:
						doc_ref = db.collection(colecao).document(colecao)
						dados = {}
						dados['Dataframe'] = df_ferramenta.to_csv(index=False)
						doc_ref.set(dados)
						st.success('Ferramenta adicionada com sucesso!')

						# Limpa cache
						caching.clear_cache()

						# flag para rodar novamente o script
						rerun = True
					except:
						st.error('Falha ao adicionar ferramenta, tente novamente ou entre em contato com suporte!')
					if rerun:
						st.experimental_rerun()
				else:
					st.error('Ferramenta com mesma identificação já inserida')
	# inclusão via planilha
	elif modo == 'Planilha':
		st.subheader('Upload de dados')
		uploaded_file = st.file_uploader("Selecione o arquivo Excel para upload")
		if uploaded_file is not None:
			data = pd.read_excel(uploaded_file, sheet_name='Parada')
			return data
		else:
			#st.error('Falha ao executar o upload do arquivo')
			pass


def write_data(df_ferramenta, colecao):
	# Armazena no banco
	try:
		doc_ref = db.collection(colecao).document(colecao)
		dados = {}
		dados['Dataframe'] = df_ferramenta.to_csv(index=False)
		doc_ref.set(dados)
		st.success('Ferramenta adicionada com sucesso!')

		# Limpa cache
		caching.clear_cache()

		# flag para rodar novamente o script
		rerun = True
	except:
		st.error('Falha ao adicionar ferramenta, tente novamente ou entre em contato com suporte!')
	if rerun:
		st.experimental_rerun()


# leitura de dados do banco
@st.cache
def load_data(colunas):
	# dicionario vazio
	dicionario = {}
	index_lc = 1

	try:
		# Define o caminho da coleção do firebase
		posts_ref = db.collection('cordax_shell')

		# Busca todos os documentos presentes na coleção e salva num dataframe
		for doc in posts_ref.stream():
			dic_auxiliar = doc.to_dict()
			dicionario[str(index_lc)] = dic_auxiliar
			index_lc += 1

		# Transforma o dicionario em dataframe
		df_lc = pd.DataFrame.from_dict(dicionario)

		# troca linhas com colunas
		df_lc = df_lc.T

		for index, row in df.iterrows():
			csv = str(row['dados'])
			csv_string = StringIO(csv)
			df_aux = pd.read_table(csv_string, sep=';')
			df2 = df2.append(df_aux, ignore_index=True)

		# Transforma string em tipo data
		df_lc['Data'] = pd.to_datetime(df_lc['Data'])

		# Ordena os dados pela data
		df_lc = df_lc.sort_values(by=['Data'], ascending=False)

		# Remove o index
		df_lc = df_lc.reset_index(drop=True)

		# Ordena as colunas
		df_lc = df_lc[colunas]
		return df_lc
	except:
		#st.info('Nao foi possivel carregar valores do banco, serao colocados valores padrao no DataFrame')
		colunas_dict = dict.fromkeys(colunas, "1")
		df_lc = pd.DataFrame.from_dict(colunas_dict, orient='index')
		return df_lc.T


# leitura de dados do banco
@st.cache(allow_output_mutation=True)
def load_colecoes(colecao, colunas):
	# dicionario vazio
	dicionario = {}

	doc_ref = db.collection(colecao).document(colecao)
	doc = doc_ref.get()

	if doc.exists:

		# Transforma o dicionario em dataframe
		dicionario = doc.to_dict()
		csv = dicionario['Dataframe']

		csv_string = StringIO(csv)
		df_lc = pd.read_table(csv_string, sep=',')

		# Transforma string em tipo data
		df_lc['Data'] = pd.to_datetime(df_lc['Data'])

		# Ordena os dados pela data
		df_lc = df_lc.sort_values(by=['Data'], ascending=False)

		# Remove o index
		df_lc = df_lc.reset_index(drop=True)

		# Ordena as colunas
		df_lc = df_lc[colunas]
		return df_lc
	else:
		return pd.DataFrame(columns=colunas)


def ajuste_dados(df):
	# seleciona a primeira linha e a transforma em coluna

	df_row0 = df[df['Status'] == 'Em Uso'].reset_index().T

	# filtra nome e data
	nome_last = str(df_row0.iloc[4, 0])
	data_last = str(df_row0.iloc[5, 0])

	# reseta index (index vira uma coluna)
	df_row0 = df_row0.reset_index()

	# Renomeia a coluna dos valores
	df_row0.rename(columns={0: "V"}, inplace=True)
	df_row0.rename(columns={'index': "Medidas"}, inplace=True)

	# retorna o nome, data e dataset organizado para ser editado e exibido no html
	return nome_last, data_last, df_row0[['Medidas', 'V']]


###########################################################################################################################################
#####								cofiguracoes aggrid											#######
###########################################################################################################################################
def config_grid(height, df, lim_min, lim_max, customizar):
	sample_size = 12
	grid_height = height

	return_mode = 'AS_INPUT'
	return_mode_value = DataReturnMode.__members__[return_mode]

	update_mode = 'VALUE_CHANGED'
	update_mode_value = GridUpdateMode.__members__[update_mode]

	# enterprise modules
	enable_enterprise_modules = False
	enable_sidebar = False

	# features
	fit_columns_on_grid_load = True
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
	if customizar:
		gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc='sum', editable=True)
		gb.configure_column("Medidas", editable=False)
		# gb.configure_column('L', editable=False)
		gb.configure_column('V', type=["numericColumn"], precision=5)

		# configures last row to use custom styles based on cell's value, injecting JsCode on components front end
		func_js = """
		function(params) {
			if (params.value > %f) {
			return {
				'color': 'black',
				'backgroundColor': 'orange'
			}
			} else if(params.value < %f) {
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
	if (selection_mode == 'multiple') & (not use_checkbox):
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


# Funcao para gerar as telas
def teste(val_max, val_min, titulo, medida, colecao, dados, conjunto):

	# carrega dados do banco de dados
	df_firebase = dados

	with t2:
		with st.beta_expander('Adicionar nova ferramenta ao sistema'):
			adicionar_ferramental(df_firebase, nomes, colecao)

	# cria dicionario vazio
	dic = {}

	df_validacao = pd.DataFrame()

	index = 0
	limits = 0

	# separa a ferramenta em uso
	ferramenta_em_uso = df_firebase.loc[(df_firebase['Status'] == 'Em Uso') & (df_firebase['Conjunto'] == str(conjunto))]

	try:
		# filtra o ultimo dado para exibir para o usuario
		nome_last, data_last, df = ajuste_dados(ferramenta_em_uso)
	except:
		t2.error('Não há ferramenta em uso')

	if ferramenta_em_uso.shape[0] > 0:
		t2.subheader('Retificar ferramenta em uso')
		for (mi, ma, med, tit) in zip(val_min, val_max, medida, titulo):

			with t2:
				gridOptions, grid_height, return_mode_value, update_mode_value, fit_columns_on_grid_load, enable_enterprise_modules = config_grid(
					62, df, mi, ma, True)
				t2.write(tit)
				response = AgGrid(
					df[df['Medidas'] == med],
					gridOptions=gridOptions,
					height=grid_height,
					width='100%',
					data_return_mode=return_mode_value,
					update_mode=update_mode_value,
					fit_columns_on_grid_load=fit_columns_on_grid_load,
					allow_unsafe_jscode=True,  # Set it to True to allow jsfunction to be injected
					enable_enterprise_modules=enable_enterprise_modules)
				df_auxiliar = response['data']
				df_validacao = pd.concat([df_validacao, df_auxiliar])
				try:
					if (df_auxiliar['V'].astype(float) > ma).any() | (df_auxiliar['V'].astype(float) < mi).any():
						limits = 1
				except:
					t2.error('Valor não conforme')

		df_validacao['V'] = pd.to_numeric(df_validacao['V'], errors='coerce')

		if df_validacao['V'].isnull().sum() > 0:
			pass
			#t2.error('Caracter invalido no campo Valor')
		else:

			df_group = df_validacao
			#df_group['Max'] = [123, 4321, 123]
			#df_group['Min'] = [0, 0, 0]
			#df_group['Resultado'] = np.where(((df_group['V'] < df_group['Max']) & (df_group['V'] > df_group['Min'])),
											# 'valido', 'invalido')

			dados_invalidos = 'invalido' in df_group.values
			if limits == 0:  # not dados_invalidos and
				# Preparando dados para escrita no banco

				dic = {}
				for index, row in df_validacao.iterrows():
					chave = row['Medidas']
					dic[chave] = str(row['V'])
				dic['Nome'] = nome
				dic['Data'] = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

				t2.info('Medidas dentro do padrao')
				submitted = t2.button('Retificar ferramenta')
				if submitted:

					ferramenta_retificada = ferramenta_em_uso
					ferramenta_retificada['Data'] = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
					ferramenta_retificada['Nome'] = nome
					ferramenta_retificada['Reformada'] = 'Sim'

					for index, row in df_validacao.iterrows():
						ferramenta_retificada[str(row['Medidas'])] = row['V']

					df_firebase.loc[df_firebase['Status'] == 'Em Uso', 'Status'] = 'Entrou em uso'
					df_firebase = df_firebase.append(ferramenta_retificada)
					write_data(df_firebase, colecao)

			else:
				t2.error('Dados invalidos')
	else:
		t2.subheader('Selecione uma ferramenta para utilizar')

		# separando as ferramentas não disponiveis
		nao_disponivel = list(df_firebase.loc[(df_firebase['Status'] != 'Disponível'), 'ID'])

		# definindo as ferramentas disponiveis
		disponiveis = df_firebase[~df_firebase['ID'].astype('str').isin(nao_disponivel)]
		id_selecionado = t2.selectbox('Ferramentas disponíveis para uso', list(disponiveis['ID']))
		selecionar = t2.button('Utilizar a ferramenta selecionada?')

		if selecionar:
			# define os dados a serem inseridos
			ferramenta_selecionada = df_firebase[df_firebase['ID'] == id_selecionado]
			ferramenta_selecionada['Data'] = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
			ferramenta_selecionada['Nome'] = nome
			ferramenta_selecionada['Status'] = 'Em Uso'
			ferramenta_selecionada['Conjunto'] = conjunto

			df_firebase = df_firebase.append(ferramenta_selecionada)
			write_data(df_firebase, colecao)
	if ferramenta_em_uso.shape[0] > 0:
		# modificar a ferramenta
		t2.subheader('Trocar ferramenta')

		# separando as ferramentas não disponiveis
		nao_disponivel = list(df_firebase.loc[(df_firebase['Status'] != 'Disponível'), 'ID'])

		# filtrando as ferramentas disponíveis
		disponiveis = df_firebase[~df_firebase['ID'].astype('str').isin(nao_disponivel)]
		id_selecionado = t2.selectbox('Ferramentas disponíveis para uso', list(disponiveis['ID']))
		selecionar = t2.button('Utilizar a ferramenta selecionada?')

		if selecionar:
			# finaliza o uso da ferramenta atual
			ferramenta_finalizada = ferramenta_em_uso
			ferramenta_finalizada['Data'] = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
			ferramenta_finalizada['Nome'] = nome
			ferramenta_finalizada['Status'] = 'Finalizada'
			df_firebase = df_firebase.append(ferramenta_finalizada)

			df_firebase.loc[df_firebase['Status'] == 'Em Uso', 'Status'] = 'Entrou em uso'

			# define os dados a serem inseridos
			ferramenta_selecionada = df_firebase[df_firebase['ID'] == id_selecionado]
			ferramenta_selecionada['Data'] = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
			ferramenta_selecionada['Nome'] = nome
			ferramenta_selecionada['Status'] = 'Em Uso'
			ferramenta_selecionada['Conjunto'] = conjunto

			df_firebase = df_firebase.append(ferramenta_selecionada)
			write_data(df_firebase, colecao)

	st.subheader('Historico de medidas')
	gridOptions, grid_height, return_mode_value, update_mode_value, fit_columns_on_grid_load, enable_enterprise_modules = config_grid(
		715, df_firebase, 0, 0, False)
	response = AgGrid(
		df_firebase,
		gridOptions=gridOptions,
		height=grid_height,
		width='100%',
		data_return_mode=return_mode_value,
		update_mode=update_mode_value,
		fit_columns_on_grid_load=fit_columns_on_grid_load,
		allow_unsafe_jscode=True,  # Set it to True to allow jsfunction to be injected
		enable_enterprise_modules=enable_enterprise_modules)

	return ferramenta_em_uso


########################################################################################################################
#####								Teste											########
########################################################################################################################

# definicao das telas da aplicacao
telas = ['DIE CORE RING',
		 'DIE CENTER PISTON',
		 'DIE CENTER PUNCH PISTON',
		 'PANEL PUNCH PISTON',
		 'PANEL PUNCH',
		 'UPPER PISTON',
		 'LOWER PISTON',
		 'CUT EDGE',
		 'BLANK DRAW',
		 'INNER PRESSURE SLEVE']

# Define as colunas do dataframe
colunas_conjunto = [
	#'Nome',				# nome do colaborador
	#				'Data',				# data da alteraçao
					'Conjunto',			# numero do conjunto
					'DCR_A',			# DIE CORE RING A
					'DCR_B',			# DIE CORE RING	B
					'DCR_C',			# DIE CORE RING C
					'PPP_A',			# PANEL PUNCH PISTON A
					'PP_A',				# PANEL PUNCH A
					'PP_B',				# PANEL PUNCH B
					'LP_A',				# LOWER PISTON A
					'LP_B',				# LOWER PISTON B
					'IPS_A',			# INNER PRESSURE SLEEVE A
					'IPS_B',			# INNER PRESSURE SLEEVE B
					'IPS_C',			# INNER PRESSURE SLEEVE C
					'DCPP_A',			# DIE CENTER PUNCH A
					'DCPP_B',			# DIE CENTER PUNCH B
					'DCP_A',			# DIE CENTER PISTON A
					'DCP_B',			# DIE CENTER PISTON B
					'CE_A',				# CUT EDGE A
					'BD_A',				# BLANK DRAW A
					'BD_B',				# BLANK DRAW B
					'UP_A',				# UPPER PISTON A
					]

dicionario_colunas = {'DCR_A':'DIE CORE RING A (DCR_A)',
					  'DCR_B':'DIE CORE RING B (DCR_B)',
					  'DCR_C':'DIE CORE RING C (DCR_C)',
					  'PPP_A':'PANEL PUNCH PISTON A (PPP_A)',
					  'PP_A':'PANEL PUNCH A (PP_A)',
					  'PP_B':'PANEL PUNCH B (PP_B)',
					  'LP_A':'LOWER PISTON A (LP_A)',
					  'LP_B':'LOWER PISTON B (LP_B)',
					  'IPS_A':'INNER PRESSURE SLEEVE A (IPS_A)',
					  'IPS_B':'INNER PRESSURE SLEEVE B (IPS_B)',
					  'IPS_C':'INNER PRESSURE SLEEVE C (IPS_C)',
					  'DCPU_A':'DIE CENTER PUNCH PISTON A (DCPP_A)',
					  'DCPU_B':'DIE CENTER PUNCH PISTON B (DCPP_B)',
					  'DCPI_A':'DIE CENTER PISTON A (DCPI_A)',
					  'DCPI_B':'DIE CENTER PISTON B (DCPI_B)',
					  'CE_A':'CUT EDGE A (CE_A)',
					  'BD_A':'BLANK DRAW A (BD_A)',
					  'BD_B':'BLANK DRAW B (BD_B)',
					  'UP_A':'UPPER PISTON A (UP_A)'}

# Menu externo ao formulario
i00, i01 = st.beta_columns([5, 16])

# define as colunas da pagina
t0, t1, html, t2 = st.beta_columns([1, 4, 9, 7])

# carrega dados do sistema
valores = [['-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', ]]
df_full = pd.DataFrame(valores, columns=colunas_conjunto)

# seleciona o conjunto
conjunto = t0.radio('Conjuntos', list(range(1, 29)))
t1.subheader('Valores atuais do conjunto')

# seleciona o ferramental
sel_tela = i01.selectbox('Selecione o ferramental', options=telas)

# Input de informacoes de nome e data
nomes = ['Mario', 'Carvalho']
nome = i00.selectbox('Nome do colaborador:', nomes)

# Leitura do banco de dados

# DIE_CORE_RING
colunas_dcr = ['ID', 'Conjunto', 'Status', 'Nome', 'Data', 'DCR_A', 'DCR_B', 'DCR_C', 'Reformada']
dados_dcr = load_colecoes('DIE_CORE_RING', colunas_dcr)
em_uso_dcr = dados_dcr.loc[(dados_dcr['Status'] == 'Em Uso') & (dados_dcr['Conjunto'] == str(conjunto))]

# PANEL_PUNCH_PISTON
colunas_ppp = ['ID', 'Conjunto', 'Status', 'Nome', 'Data', 'PPP_A', 'Reformada']
dados_ppp = load_colecoes('PANEL_PUNCH_PISTON', colunas_ppp)
em_uso_ppp = dados_ppp.loc[(dados_ppp['Status'] == 'Em Uso') & (dados_ppp['Conjunto'] == str(conjunto))]

# PANEL_PUNCH
colunas_pp = ['ID', 'Conjunto', 'Status', 'Nome', 'Data', 'PP_A', 'PP_B', 'Reformada']
dados_pp = load_colecoes('PANEL_PUNCH', colunas_pp)
em_uso_pp = dados_pp.loc[(dados_pp['Status'] == 'Em Uso') & (dados_pp['Conjunto'] == str(conjunto))]

# LOWER_PISTON
colunas_lp = ['ID', 'Conjunto', 'Status', 'Nome', 'Data', 'LP_A', 'LP_B', 'Reformada']
dados_lp = load_colecoes('LOWER_PISTON', colunas_lp)
em_uso_lp = dados_lp.loc[(dados_lp['Status'] == 'Em Uso') & (dados_lp['Conjunto'] == str(conjunto))]

# CUT_EDGE
colunas_ce = ['ID', 'Conjunto', 'Status', 'Nome', 'Data', 'CE_A', 'Reformada']
dados_ce = load_colecoes('CUT_EDGE', colunas_ce)
em_uso_ce = dados_ce.loc[(dados_ce['Status'] == 'Em Uso') & (dados_ce['Conjunto'] == str(conjunto))]

# BLANK_DRAW
colunas_bd = ['ID', 'Conjunto', 'Status', 'Nome', 'Data', 'BD_A', 'BD_B', 'Reformada']
dados_bd = load_colecoes('BLANK_DRAW', colunas_bd)
em_uso_bd = dados_bd.loc[(dados_bd['Status'] == 'Em Uso') & (dados_bd['Conjunto'] == str(conjunto))]

# DIE_CENTER_PUNCH_PISTON
colunas_dcpp = ['ID', 'Conjunto', 'Status', 'Nome', 'Data', 'DCPP_A', 'DCPP_B', 'Reformada']
dados_dcpp = load_colecoes('DIE_CENTER_PUNCH_PISTON', colunas_dcpp)
em_uso_dcpp = dados_dcpp.loc[(dados_dcpp['Status'] == 'Em Uso') & (dados_dcpp['Conjunto'] == str(conjunto))]

# DIE_CENTER_PISTON
colunas_dcp = ['ID', 'Conjunto', 'Status', 'Nome', 'Data', 'DCP_A', 'DCP_B', 'Reformada']
dados_dcp = load_colecoes('DIE_CENTER_PISTON', colunas_dcp)
em_uso_dcp = dados_dcp.loc[(dados_dcp['Status'] == 'Em Uso') & (dados_dcp['Conjunto'] == str(conjunto))]

# INNER_PRESSURE_SLEVE
colunas_ips = ['ID', 'Conjunto', 'Status', 'Nome', 'Data', 'IPS_A', 'IPS_B', 'IPS_C', 'Reformada']
dados_ips = load_colecoes('INNER_PRESSURE_SLEVE', colunas_ips)
em_uso_ips = dados_ips.loc[(dados_ips['Status'] == 'Em Uso') & (dados_ips['Conjunto'] == str(conjunto))]

# UPPER_PISTON
colunas_up = ['ID', 'Conjunto', 'Status', 'Nome', 'Data', 'UP_A', 'Reformada']
dados_up = load_colecoes('UPPER_PISTON', colunas_up)
em_uso_up = dados_up.loc[(dados_up['Status'] == 'Em Uso') & (dados_up['Conjunto'] == str(conjunto))]

df_full.iloc[0,0]	= conjunto					# numero do conjunto
if em_uso_dcr.shape[0] > 0:
	df_full.iloc[0,1]	= em_uso_dcr.iloc[0,5]		# DIE CORE RING A
	df_full.iloc[0,2]	= em_uso_dcr.iloc[0,6]		# DIE CORE RING	B
	df_full.iloc[0,3]	= em_uso_dcr.iloc[0,7]		# DIE CORE RING C

if em_uso_ppp.shape[0] > 0:
	df_full.iloc[0,4]	= em_uso_ppp.iloc[0,5]		# PANEL PUNCH PISTON A

if em_uso_pp.shape[0] > 0:
	df_full.iloc[0,5]	= em_uso_pp.iloc[0,5]		# PANEL PUNCH A
	df_full.iloc[0,6]	= em_uso_pp.iloc[0,6]		# PANEL PUNCH B

if em_uso_lp.shape[0] > 0:
	df_full.iloc[0,7]	= em_uso_lp.iloc[0,5]		# LOWER PISTON A
	df_full.iloc[0,8]	= em_uso_lp.iloc[0,6]		# LOWER PISTON B

if em_uso_ips.shape[0] > 0:
	df_full.iloc[0,9]	= em_uso_ips.iloc[0,5]		# INNER PRESSURE SLEEVE A
	df_full.iloc[0,10]	= em_uso_ips.iloc[0,6]		# INNER PRESSURE SLEEVE B
	df_full.iloc[0,11]	= em_uso_ips.iloc[0,7]		# INNER PRESSURE SLEEVE C

if em_uso_dcpp.shape[0] > 0:
	df_full.iloc[0,12]	= em_uso_dcpp.iloc[0,5]		# DIE CENTER PUNCH A
	df_full.iloc[0,13]	= em_uso_dcpp.iloc[0,6]		# DIE CENTER PUNCH B

if em_uso_dcp.shape[0] > 0:
	df_full.iloc[0,14]	= em_uso_dcp.iloc[0,5]		# DIE CENTER PISTON A
	df_full.iloc[0,15]	= em_uso_dcp.iloc[0,6]		# DIE CENTER PISTON B

if em_uso_ce.shape[0] > 0:
	df_full.iloc[0,16]	= em_uso_ce.iloc[0,5]		# CUT EDGE A

if em_uso_bd.shape[0] > 0:
	df_full.iloc[0,17]	= em_uso_bd.iloc[0,5]		# BLANK DRAW A
	df_full.iloc[0,18]	= em_uso_bd.iloc[0,6]		# BLANK DRAW B

if em_uso_up.shape[0] > 0:
	df_full.iloc[0,19]	= em_uso_up.iloc[0,5]		# UPPER PISTON A

t1.write(df_full.T)

# Tela DIE CORE RING
if sel_tela == 'DIE CORE RING':

	# input de limites e das colunas do data frame
	val_max = [4.2777, 2.2810, 1.8752]
	val_min = [4.2773, 2.2800, 1.8750]
	titulo = ['DCR_A: (4.2773 até 4.2777)', 'DCR_B: (2.2800 até 2.2810)', 'DCR_C: (1.8750 até 1.8752)']
	medida = ['DCR_A', 'DCR_B', 'DCR_C']

	#dados = load_colecoes('DIE_CORE_RING', colunas)
	ferramenta_em_uso = teste(val_max, val_min, titulo, medida,'DIE_CORE_RING', dados_dcr, conjunto)

	# carrega pagina html
	htmlfile = open('DIE_CORE_RING.html', 'r', encoding='utf-8')
	source = htmlfile.read()

	# carrega imagem da tela do cordax
	file_ = open("DIE_CORE_RING.png", "rb")
	contents = file_.read()
	data_url = base64.b64encode(contents).decode("utf-8")
	file_.close()

	# HTML: html com imagens e dados
	with html:
		if ferramenta_em_uso.shape[0] > 0:
			components.html(source.format(image=data_url,
										  v0=ferramenta_em_uso.iloc[0, 5],
										  v1=ferramenta_em_uso.iloc[0, 6],
										  v2=ferramenta_em_uso.iloc[0, 7],
										  nome='Última alteração feita por: ' + ferramenta_em_uso.iloc[0, 3],
										  data='Data: ' + str(ferramenta_em_uso.iloc[0, 4])), height=775)
		else:
			components.html(source.format(image=data_url,
										  v0='',
										  v1='',
										  v2='',
										  nome='Última alteração feita por: ',
										  data='Data: '), height=775)

# Tela INNER PRESSURE SLEVE
if sel_tela == 'INNER PRESSURE SLEVE':

	# input de limites e das colunas do data frame

	val_max = [1.6980, 2.126, 1.8347]
	val_min = [1.6970, 2.124, 1.8345]
	titulo = ['IPS_A: (1.6970 até 1.6980)', 'IPS_B: (2.124 até 2.126)', 'IPS_C: (1.8345 até 1.8347)']
	medida = ['IPS_A', 'IPS_B', 'IPS_C']

	#dados = load_colecoes('INNER_PRESSURE_SLEVE', colunas)
	ferramenta_em_uso = teste(val_max, val_min, titulo, medida,'INNER_PRESSURE_SLEVE', dados_ips, conjunto)

	# carrega pagina html
	htmlfile = open('INNER_PRESSURE_SLEVE.html', 'r', encoding='utf-8')
	source = htmlfile.read()

	# carrega imagem da tela do cordax
	file_ = open("INNER_PRESSURE_SLEVE.png", "rb")
	contents = file_.read()
	data_url = base64.b64encode(contents).decode("utf-8")
	file_.close()

	# HTML: html com imagens e dados
	with html:
		if ferramenta_em_uso.shape[0] > 0:
			components.html(source.format(image=data_url,
										  v0=ferramenta_em_uso.iloc[0, 5],
										  v1=ferramenta_em_uso.iloc[0, 6],
										  v2=ferramenta_em_uso.iloc[0, 7],
										  nome='Última alteração feita por: ' + ferramenta_em_uso.iloc[0, 3],
										  data='Data: ' + str(ferramenta_em_uso.iloc[0, 4])), height=775)
		else:
			components.html(source.format(image=data_url,
										  v0='',
										  v1='',
										  v2='',
										  nome='Última alteração feita por: ',
										  data='Data: '), height=775)

if sel_tela == 'PANEL PUNCH PISTON':
	# input de limites e das colunas do data frame
	val_max = [1.0405]
	val_min = [1.0395]
	titulo = ['PPP_A: (1.0395 até 1.0405)']
	medida = ['PPP_A']

	ferramenta_em_uso = teste(val_max, val_min, titulo, medida,'PANEL_PUNCH_PISTON', dados_ppp, conjunto)

	# carrega pagina html
	htmlfile = open('PANEL_PUNCH_PISTON.html', 'r', encoding='utf-8')
	source = htmlfile.read()

	# carrega imagem da tela do cordax
	file_ = open("PANEL_PUNCH_PISTON.png", "rb")
	contents = file_.read()
	data_url = base64.b64encode(contents).decode("utf-8")
	file_.close()

	# HTML: html com imagens e dados
	with html:
		if ferramenta_em_uso.shape[0] > 0:
			components.html(source.format(image=data_url,
										  v0=ferramenta_em_uso.iloc[0, 5],
										  nome='Última alteração feita por: ' + ferramenta_em_uso.iloc[0, 3],
										  data='Data: ' + str(ferramenta_em_uso.iloc[0, 4])), height=775)
		else:
			components.html(source.format(image=data_url,
										  v0='',
										  nome='Última alteração feita por: ',
										  data='Data: '), height=775)

if sel_tela == 'UPPER PISTON':

	# input de limites e das colunas do data frame
	val_max = [2.8420]
	val_min = [2.8410]
	titulo = ['UP_A: (2.8410 até 2.8420)']
	medida = ['UP_A']

	ferramenta_em_uso = teste(val_max, val_min, titulo, medida,'UPPER_PISTON', dados_up, conjunto)

	# carrega pagina html
	htmlfile = open('UPPER_PISTON.html', 'r', encoding='utf-8')
	source = htmlfile.read()

	# carrega imagem da tela do cordax
	file_ = open("UPPER_PISTON.png", "rb")
	contents = file_.read()
	data_url = base64.b64encode(contents).decode("utf-8")
	file_.close()

	# HTML: html com imagens e dados
	with html:
		if ferramenta_em_uso.shape[0] > 0:
			components.html(source.format(image=data_url,
										  v0=ferramenta_em_uso.iloc[0, 5],
										  nome='Última alteração feita por: ' + ferramenta_em_uso.iloc[0, 3],
										  data='Data: ' + str(ferramenta_em_uso.iloc[0, 4])), height=775)
		else:
			components.html(source.format(image=data_url,
										  v0='',
										  nome='Última alteração feita por: ',
										  data='Data: '), height=775)

if sel_tela == 'DIE CENTER PISTON':

	# input de limites e das colunas do data frame
	val_max = [3.2857, 2.6370]
	val_min = [3.2847, 2.6360]
	titulo = ['DCP_A: (3.2847 até 3.2857)', 'DCP_B: (2.6360 até 2.6370)']
	medida = ['DCP_A', 'DCP_B']

	ferramenta_em_uso = teste(val_max, val_min, titulo, medida, 'DIE_CENTER_PISTON', dados_dcp, conjunto)

	# carrega pagina html
	htmlfile = open('DIE_CENTER_PISTON.html', 'r', encoding='utf-8')
	source = htmlfile.read()

	# carrega imagem da tela do cordax
	file_ = open("DIE_CENTER_PISTON.png", "rb")
	contents = file_.read()
	data_url = base64.b64encode(contents).decode("utf-8")
	file_.close()

	# HTML: html com imagens e dados
	with html:
		if ferramenta_em_uso.shape[0] > 0:
			components.html(source.format(image=data_url,
										  v0=ferramenta_em_uso.iloc[0, 5],
										  v1=ferramenta_em_uso.iloc[0, 6],
										  nome='Última alteração feita por: ' + ferramenta_em_uso.iloc[0, 3],
										  data='Data: ' + str(ferramenta_em_uso.iloc[0, 4])), height=775)
		else:
			components.html(source.format(image=data_url,
										  v0='',
										  v1='',
										  nome='Última alteração feita por: ',
										  data='Data: '), height=775)

if sel_tela == 'DIE CENTER PUNCH PISTON':

	# input de limites e das colunas do data frame
	val_max = [1.0001, 1.8200]
	val_min = [0.9999, 1.8195]
	titulo = ['DCPP_A: (0.9999 até 1.0001)', 'DCPP_B: (1.8195 até 1.8200)']
	medida = ['DCPP_A', 'DCPP_B']

	ferramenta_em_uso = teste(val_max, val_min, titulo, medida, 'DIE_CENTER_PUNCH_PISTON', dados_dcpp, conjunto)

	# carrega pagina html
	htmlfile = open('DIE_CENTER_PUNCH.html', 'r', encoding='utf-8')
	source = htmlfile.read()

	# carrega imagem da tela do cordax
	file_ = open("DIE_CENTER_PUNCH.png", "rb")
	contents = file_.read()
	data_url = base64.b64encode(contents).decode("utf-8")
	file_.close()

	# HTML: html com imagens e dados
	with html:
		if ferramenta_em_uso.shape[0] > 0:
			components.html(source.format(image=data_url,
										  v0=ferramenta_em_uso.iloc[0, 5],
										  v1=ferramenta_em_uso.iloc[0, 6],
										  nome='Última alteração feita por: ' + ferramenta_em_uso.iloc[0, 3],
										  data='Data: ' + str(ferramenta_em_uso.iloc[0, 4])), height=775)
		else:
			components.html(source.format(image=data_url,
										  v0='',
										  v1='',
										  nome='Última alteração feita por: ',
										  data='Data: '), height=775)

if sel_tela == 'PANEL PUNCH':

	# input de limites e das colunas do data frame
	val_max = [0.6548, 1.8840]
	val_min = [0.6546, 1.8835]
	titulo = ['PP_A: (0.6546 até 0.6548)', 'PP_B: (1.8835 até 1.8840)']
	medida = ['PP_A', 'PP_B']

	ferramenta_em_uso = teste(val_max, val_min, titulo, medida, 'PANEL_PUNCH', dados_pp, conjunto)

	# carrega pagina html
	htmlfile = open('PANEL_PUNCH.html', 'r', encoding='utf-8')
	source = htmlfile.read()

	# carrega imagem da tela do cordax
	file_ = open("PANEL_PUNCH.png", "rb")
	contents = file_.read()
	data_url = base64.b64encode(contents).decode("utf-8")
	file_.close()

	# HTML: html com imagens e dados
	with html:
		if ferramenta_em_uso.shape[0] > 0:
			components.html(source.format(image=data_url,
										  v0=ferramenta_em_uso.iloc[0, 5],
										  v1=ferramenta_em_uso.iloc[0, 6],
										  nome='Última alteração feita por: ' + ferramenta_em_uso.iloc[0, 3],
										  data='Data: ' + str(ferramenta_em_uso.iloc[0, 4])), height=775)
		else:
			components.html(source.format(image=data_url,
										  v0='',
										  v1='',
										  nome='Última alteração feita por: ',
										  data='Data: '), height=775)

if sel_tela == 'LOWER PISTON':

	# input de limites e das colunas do data frame
	val_max = [1.1870, 0.7030]
	val_min = [1.1860, 0.7000]
	titulo = ['LP_A: (1.1860 até 1.1870)', 'LP_B: (0.7000 até 0.7030)']
	medida = ['LP_A', 'LP_B']

	ferramenta_em_uso = teste(val_max, val_min, titulo, medida, 'LOWER_PISTON', dados_lp, conjunto)

	# carrega pagina html
	htmlfile = open('LOWER_PISTON.html', 'r', encoding='utf-8')
	source = htmlfile.read()

	# carrega imagem da tela do cordax
	file_ = open("LOWER_PISTON.png", "rb")
	contents = file_.read()
	data_url = base64.b64encode(contents).decode("utf-8")
	file_.close()

	# HTML: html com imagens e dados
	with html:
		if ferramenta_em_uso.shape[0] > 0:
			components.html(source.format(image=data_url,
										  v0=ferramenta_em_uso.iloc[0, 5],
										  v1=ferramenta_em_uso.iloc[0, 6],
										  nome='Última alteração feita por: ' + ferramenta_em_uso.iloc[0, 3],
										  data='Data: ' + str(ferramenta_em_uso.iloc[0, 4])), height=775)
		else:
			components.html(source.format(image=data_url,
										  v0='',
										  v1='',
										  nome='Última alteração feita por: ',
										  data='Data: '), height=775)

if sel_tela == 'BLANK DRAW':

	# input de limites e das colunas do data frame
	val_max = [2.8510, 2.3915]
	val_min = [2.8508, 2.3905]
	titulo = ['BD_A: (2.8508 até 2.8510)', 'BD_B: (2.3905 até 2.3915)']
	medida = ['BD_A', 'BD_B']

	ferramenta_em_uso = teste(val_max, val_min, titulo, medida, 'BLANK_DRAW', dados_bd, conjunto)

	# carrega pagina html
	htmlfile = open('BLANK_DRAW.html', 'r', encoding='utf-8')
	source = htmlfile.read()

	# carrega imagem da tela do cordax
	file_ = open("BLANK_DRAW.png", "rb")
	contents = file_.read()
	data_url = base64.b64encode(contents).decode("utf-8")
	file_.close()

	# HTML: html com imagens e dados
	with html:
		if ferramenta_em_uso.shape[0] > 0:
			components.html(source.format(image=data_url,
										  v0=ferramenta_em_uso.iloc[0, 5],
										  v1=ferramenta_em_uso.iloc[0, 6],
										  nome='Última alteração feita por: ' + ferramenta_em_uso.iloc[0, 3],
										  data='Data: ' + str(ferramenta_em_uso.iloc[0, 4])), height=775)
		else:
			components.html(source.format(image=data_url,
										  v0='',
										  v1='',
										  nome='Última alteração feita por: ',
										  data='Data: '), height=775)

if sel_tela == 'CUT EDGE':

	# input de limites e das colunas do data frame
	val_max = [1.1877]
	val_min = [1.1873]
	titulo = ['CE_A: (1.1877 até 1.1873)']
	medida = ['CE_A']

	ferramenta_em_uso = teste(val_max, val_min, titulo, medida, 'CUT_EDGE', dados_ce, conjunto)

	# carrega pagina html
	htmlfile = open('CUT_EDGE.html', 'r', encoding='utf-8')
	source = htmlfile.read()

	# carrega imagem da tela do cordax
	file_ = open("CUT_EDGE.png", "rb")
	contents = file_.read()
	data_url = base64.b64encode(contents).decode("utf-8")
	file_.close()

	# HTML: html com imagens e dados
	with html:
		if ferramenta_em_uso.shape[0] > 0:
			components.html(source.format(image=data_url,
										  v0=ferramenta_em_uso.iloc[0, 5],
										  nome='Última alteração feita por: ' + ferramenta_em_uso.iloc[0, 3],
										  data='Data: ' + str(ferramenta_em_uso.iloc[0, 4])), height=775)
		else:
			components.html(source.format(image=data_url,
										  v0='',
										  nome='Última alteração feita por: ',
										  data='Data: '), height=775)