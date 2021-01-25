import requests
import re


def main(matricula_local, localizador_local, station):
	global headers
	headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'}
	if Connection():
		global first_date, second_date
		data2 = {}
		months = {'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4, 'mayo': 5, 'junio': 6, 'julio': 7, 'agosto': 8, 'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12}
		list_names = ('org.apache.struts.taglib.html.TOKEN', 'id', 'localizador', 'matricula', 'matriculaRemolque', 'idEstacion', 'estacion', 'fechaCita', 'horaCita', 'nombreVehiculo', 'nombreRemolque', 'nombreTipoInspeccionRemolque', 'nombreTipoInspeccion', 'nombreTipoInspeccion', 'numeroInspeccion', 'nombre', 'apellido1', 'apellido2', 'telefono', 'codigoPostal', 'email', 'tipo_autoreparacion', 'tipo_taller', 'taller', 'cifTaller', 'tipo_autoreparacion_rem', 'tipo_taller_rem', 'taller_rem', 'cifTaller_rem', 'version')
		first_date = []
		second_date = []
		
		"""Acepta el pop up que tienen"""
		
		url = 'https://www.itvcita.com/registroCheckMovil.do'
		response = s.post(url, headers = headers, data = data, cookies = cookies)

		"""Inicia sesión"""
		
		url = 'https://www.itvcita.com/accesoCancelarCita.do'
		data['org.apache.struts.taglib.html.TOKEN'] = data.pop('t')
		data['modificaCita'] = 1
		data['localizador'] = localizador_local
		data['matriculaAnulacion'] = matricula_local
		response = s.post(url, headers = headers, data = data, cookies = cookies)
		error = re.findall(r'"mensaje error"', response.content.decode())
		if len(error) > 0:
			return "InvalidData"
			Close()
		counter = 0
		
		"""Consigue los datos de la cita actual"""
		
		try:
			for i in re.findall(r'value=".*"', response.content.decode()):
				value = i[:i.find('"', 7) + 1].split('"')
				if len(value[1]) == 0:
					data2[list_names[counter]] = ''				
				else:
					if value[1].count(',') == 2:
						date = value[1].split(',')
						date2 = date[1].split(' ')
						first_date.append(int(date2[1])) #Día
						first_date.append(months[date2[2]]) #Mes
						first_date.append(int(date[2].strip())) #Año
						data2[list_names[counter]] = value[1]
					else:
						data2[list_names[counter]] = value[1]
				counter += 1
		except IndexError:
			pass
		
		"""Recorre los pasos a seguir"""

		url = 'https://www.itvcita.com/modificaCitaPaso1.do'
		response = s.post(url, headers = headers, cookies = cookies, data = data2)

		"""Introduce los datos necesarios para mirar una fecha más reciente"""
		
		url = 'https://www.itvcita.com/solicitudCitaPaso2.do'
		data.pop('modificaCita')
		data.pop('localizador')
		data.pop('matriculaAnulacion')
		data['remolque'] = 'false'
		data['tipoInspeccionVeh'] = 'periodica'
		response = s.post(url, cookies = cookies, headers = headers, data = data)
		
		"""Recoge los datos de la cita más reciente"""

		url = 'https://www.itvcita.com/calcularDiaProximaCita.do'
		data.pop('remolque')
		data.pop('tipoInspeccionVeh')
		data['idEstacion'] = station
		response = s.post(url, cookies = cookies, headers = headers, data = data)
		value = response.content.decode()
		if value != 'No hay disponibles.':
			date = value.split(',')[1]
			date = date.split(' ')
			date.pop(0)
			date2 = value.split(',')[2]
			date2 = date2.strip(' ')
			date.append(date2)
			second_date = date
			second_date[1] = months[second_date[1]]
			second_date[0] = int(second_date[0])
			second_date[2] = int(second_date[2])
			return Comparator()
		
		else:
			return value

		
		
	else:
		return "NoInternet"

def Connection():
	"""Comprueba la disponibilidad de Internet"""
	global cookies, data, s
	s = requests.Session()
	url = 'https://www.itvcita.com/Welcome.do'
	data = {}
	try:
		response = s.get(url, headers=headers)
		cookies = s.cookies.get_dict()
		data['t'] = re.findall(r'value="\w{32}"', response.content.decode())[0][7:-1]
		return True
	except requests.ConnectionError:
		return False

def Comparator():
	"""Compara entre las dos fechas si la actual es más reciente o no"""
	if second_date[2] < first_date[2]:
		return Alarm()
	elif second_date[2] == first_date[2]:
		if second_date[1] < first_date[1]:
			return Alarm()
		elif second_date[1] == first_date[1]:
			if second_date[0] < first_date[0]:
				return Alarm()
			elif second_date[0] == first_date[0]:
				return "SameDate"
			else:
				return "NoBetter"
		else:
			return "NoBetter"
	else:
		return "NoBetter"


def Alarm():
	return "BetterDate"

def Close():
	s.keep_alive = False