def trata_dados(data, tipo):

	# tratamento da planilha de tampas prata
	data.rename(columns={data.columns[0]: "remove"}, inplace=True)
	data.dropna(subset=['remove'], inplace=True)
	data.rename(columns=data.iloc[0].str.strip(), inplace=True)
	data.reset_index(drop=True, inplace=True)
	data.drop([0], inplace=True)
	data.rename(columns={data.columns[17]: "observacao"}, inplace=True)
	data = data.loc[(data['STATUS'].str.lower() == 'armazenada') & (pd.isna(data['observacao']))]
	data = data.iloc[:, [2, 6, 1, 0, 4, 3, 14, 15, 16]]
	
	dicionario_colunas = {
		data.columns[0]: "numero_OT",
		data.columns[1]: "data",
		data.columns[2]: "tipo_bobina",
		data.columns[3]: "codigo_bobina",
		data.columns[4]: "peso_bobina",
		data.columns[5]: "codigo_SAP",
		data.columns[6]: "data_entrada",
		data.columns[7]: "paletes_gerados",
		data.columns[8]: "status"	
	}
	
	data.rename(columns=dicionario_colunas, inplace=True)
	
	data.codigo_SAP = data.codigo_bobina
	
	# define o tipo de tampa de acordo com o parametro tipo
	if tipo == 1:
		data.tipo_bobina = 'Tampa Prata'
	elif tipo == 2:
		data.tipo_bobina = 'Tampa Dourada'
	elif tipo == 3:
		data.tipo_bobina = 'Tampa Branca'
	elif tipo == 4:
		data.tipo_bobina = 'Tampa Lacre Azul'
		
	data.data_entrada = '-'
	data.paletes_gerados = (data['peso_bobina']) * 412 / 187200
	data.paletes_gerados = data.paletes_gerados.astype('int')
	data.status = 'Disponível'
	return data


def upload_excel(uploaded_file):
	# Leitura dos dados do arquivo excel
	try:
		# tratamento da planilha de tampas prata
		# st.subheader('Bobina Disponíveis: Tampa Prata')
		df_tp = pd.read_excel(uploaded_file, sheet_name='Bobina Tampa Prata')
		tratado_tp = trata_dados(df_tp, 1)
		# st.write(tratado_tp.head(10))

		# tratamento da planilha de tampass gold
		# st.subheader('Bobina Disponíveis: Tampa Dourada')
		df_gd = pd.read_excel(uploaded_file, sheet_name='Bobina Tampa Gold')
		tratado_gd = trata_dados(df_gd, 2)
		# st.write(tratado_gd.head(10))

		# tratamento da palnilha de tampas brancas
		# st.subheader('Bobina Disponíveis: Tampa Branca')
		df_br = pd.read_excel(uploaded_file, sheet_name='BOBINA TAMPA BRANCA')
		tratado_br = trata_dados(df_br, 3)
		# st.write(tratado_br.head(10))

		# tratamento da planilha de tampas de lacre azul
		# st.subheader('Bobina Disponíveis: Tampa Lacre Azul')
		df_ta = pd.read_excel(uploaded_file, sheet_name='Bobina Tampa Lacre Azul')
		tratado_ta = trata_dados(df_ta, 4)
		# st.write(tratado_ta.head(10))

		dados = tratado_tp.append(tratado_gd, ignore_index=True)
		dados = dados.append(tratado_br, ignore_index=True)
		dados = dados.append(tratado_ta, ignore_index=True)
		
		# st.subheader('Bobinas Filtradas')
		# st.write(dados)

		return dados
	except:
		st.error('Arquivo não compatível')
	return None


def insert_excel(df):
	try:
		# lista de bobinas ja inclusas no sistema
		bobinas_antigas = df_bobinas.numero_OT

		df.numero_OT = df.numero_OT.astype(str)

		# Filtrando os dados (tempo maior que 30 e eventos incluídos em tipo)
		st.subheader('Bobinas a serem inseridas')
		
		df = df[~df['numero_OT'].isin(list(bobinas_antigas))]

		# Se houver variáveis a serem incluídas e faz a inclusão
		if df.shape[0] > 0:
			st.write('Confira os dados antes de inserí-los no sistema. Valores "nan" indicam que faltam dados e a planilha deve ser corrigida.')
			st.write(df)
			batch = db.batch()
			for index, row in df.iterrows():

				# Define a quantidade de paletes que podem ser gerados pela bobina
				qtd_paletes = row.paletes_gerados

				# cria dataframe e preenche com os dados da bobina
				df_paletes_sem = pd.DataFrame(columns=col_pal_sem, index=list(range(qtd_paletes)))
				df_paletes_sem['numero_OT'] = str(row['numero_OT'])
				df_paletes_sem['tipo_tampa'] = str(row['tipo_bobina'])
				df_paletes_sem['data_gerado'] = str(row['data_entrada'])
				df_paletes_sem['data_estoque'] = '-'
				df_paletes_sem['data_consumo'] = '-'
				df_paletes_sem['codigo_tampa_SAP'] = '-'
				df_paletes_sem['numero_palete'] = '-'

				# for para iterar sobre todos os paletes e salvar
				for index, rows in df_paletes_sem.iterrows():
					if index < 10:
						 index_str = '0' + str(index)
					else:
						 index_str = str(index)
					rows['documento'] = index_str

				row['Paletes'] = df_paletes_sem.to_csv()
				ref = db.collection('Bobina').document(row['numero_OT'])
				row_string = row.astype(str)
				batch.set(ref, row_string.to_dict())
			
			inserir = st.button('Inserir os dados no sistema?')
			
			if inserir:
				# escreve os dados no servidor
				batch.commit()	

				# Limpa cache
				caching.clear_cache()		
				return df
			return None
		else:
			st.info('Todas as bobinas filtradas da planilha já estão inseridas no sistema!')
			return None
	except:
		st.error('Dados não inseridos no banco')
		return None
	#pass

	
def local_css(file_name):
	with open(file_name) as f:
		st.markdown('<style>{}</style>'.format(f.read()), unsafe_allow_html=True)

local_css("style.css")	


# Define cores para os valores validos ou invalidos
def color(val):
	if val == 'invalido':
		cor = 'red'
	else:
		cor = 'white'
	return 'background-color: %s' % cor


# Gera arquivo excel
def to_excel(df):
	output = BytesIO()
	writer = pd.ExcelWriter(output, engine='xlsxwriter')
	df.to_excel(writer, sheet_name='Sheet1')
	writer.save()
	processed_data = output.getvalue()
	return processed_data


# Gera o link para o download do excel
def get_table_download_link(df):
	"""Generates a link allowing the data in a given panda dataframe to be downloaded
	in:  dataframe
	out: href string
	"""
	val = to_excel(df)
	b64 = base64.b64encode(val)  # val looks like b'...'
	return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="dados.xlsx">Download dos dados em Excel</a>'  # decode b'abc' => abc


# visualizar pdf
def show_pdf(file_path):
	with open(file_path,"rb") as f:
		base64_pdf = base64.b64encode(f.read()).decode('utf-8')
	pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf">'
	st.markdown(pdf_display, unsafe_allow_html=True)


def download_etiqueta(data, tipo): # 0 sem selante e 1 com selante

	# carrega arquivo excel base para etiqueta
	wb = load_workbook('teste2.xlsx')

	# seleciona a planilha
	ws = wb.active

	# converte string para datetime
	data['data_estoque'] = pd.to_datetime(data['data_estoque'])

	# sem selante
	if tipo == 0:
		# Preenchimento dos valores
		ws['A7'] = str(data['tipo_tampa'])  # 'tipo produto'
		ws['B7'] = 'Sem selante'  # 'com/sem selante'
		ws['A9'] = 'definir codigo produto'  # 'codigo produto'
		ws['B13'] = str(data['numero_OT'])  # numero da bobina
	else:
		# Preenchimento dos valores
		ws['A7'] = str(data['codigo_SAP'])  # 'tipo produto'
		ws['B7'] = 'Com selante'  # 'com/sem selante'
		ws['A9'] = 'definir codigo produto'  # 'codigo produto'
		ws['B13'] = str(data['numero_lote'])  # numero da bobina

	# pega a hora que o palete foi para o estoque
	horario = datetime.time(data['data_estoque'])

	# Adequa os valores dos turnos
	if (horario >= time(23, 0, 0)) and (horario < time(7, 0, 0)):
		ws['B11'] = 'A'  # 'turno'
	elif (horario >= time(7, 0, 0)) and (horario < time(15, 0, 0)):
		ws['B11'] = 'B'  # 'turno'
	else:
		ws['B11'] = 'C'  # 'turno'

	ws['A11'] = data['data_estoque']  # 'data'
	ws['C11'] = data['data_estoque']  # 'hora'
	ws['C9'] = data['numero_palete']  # numero etiqueta

	wb.save('teste.xlsx')
	stream = BytesIO()
	wb.save(stream)
	towrite = stream.getvalue()
	b64 = base64.b64encode(towrite).decode()  # some strings

	# link para download e nome do arquivo

	#t = "<div>Hello there my <span class='highlight blue'>name <span class='bold'>yo</span> </span> is <span class='highlight red'>Fanilo <span class='bold'>Name</span></span></div>"
	#st.markdown(t, unsafe_allow_html=True)

	linko = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="myfilename.xlsx"><span class="highlight blue">Download etiqueta</span></a>'
	st.markdown(linko, unsafe_allow_html=True)


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
		df2['numero_OT'] = df2['numero_OT'].astype('str')

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
		df2['numero_lote'] = df2['numero_lote'].astype('str')

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
		dic['tipo_bobina'] = s2.selectbox('Tipo da bobina', list(tipos_bobinas.keys()))
		dic['codigo_bobina'] = s3.text_input('Codigo da bobina')
		dic['peso_bobina'] = s4.number_input('Peso da bobina', step=100, format='%i', value=9000, max_value=18000)
		dic['codigo_SAP'] = s5.text_input('Código SAP')
		dic['data_entrada'] = ''
		submitted = s6.form_submit_button('Adicionar bobina ao sistema')

	if submitted:
		# verifica se ja existe bobina com o numero de lote inserido
		if df_pal_sem[df_pal_sem['numero_OT'] == (dic['numero_OT'])].shape[0] == 0:
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
		else:
			st.error('Já existe bobina com o número do lote informado')

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
		dic['peso_vedante'] = s3.number_input('Peso do vedante', step=100, format='%i', value=5000, max_value=10000)
		dic['lote_interno'] = s4.text_input('Lote interno')
		dic['data_entrada'] = ''
		submitted = s5.form_submit_button('Adicionar selante ao sistema')

	if submitted:
		# verifica se ja existe selante com o numero de lote inserido
		if df_pal_com[df_pal_com['numero_lote'] == (dic['numero_lote'])].shape[0] == 0:
			# Transforma dados do formulário em um dicionário
			keys_values = dic.items()
			new_d = {str(key): str(value) for key, value in keys_values}

			# Verifica campos não preenchidos e os modifica
			for key, value in new_d.items():
				if (value == '') or value == '[]':
					new_d[key] = '-'

			# define a quantidade de paletes gerados pelo selante
			new_d['paletes_gerados'] = int(int(new_d['peso_vedante']) * 2857 / 187200)

			# Define a quantidade de paletes que podem ser gerados pelo selante
			qtd_paletes = int(new_d['paletes_gerados'])

			# cria dataframe e preenche com os dados da selante
			df_paletes_selante = pd.DataFrame(columns=col_pal_sel, index=list(range(qtd_paletes)))
			df_paletes_selante['numero_lote'] = str(new_d['numero_lote'])
			df_paletes_selante['codigo_SAP'] = str(new_d['codigo_SAP'])
			df_paletes_selante['data_gerado'] = str(new_d['data_entrada'])
			df_paletes_selante['tipo_tampa']
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
				st.success('Selante adicionada com sucesso!')

				# Limpa cache
				caching.clear_cache()

				# flag para rodar novamente o script
				rerun = True
			except:
				st.error('Falha ao adicionar selante, tente novamente ou entre em contato com suporte!')

			if rerun:
				st.experimental_rerun()
		else:
			st.error('Já existe selante com o número do lote informado')
###########################################################################################################################################
#####								cofiguracoes aggrid											#######
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
