from mrjob.job import MRJob
from mrjob.step import MRStep

TIPOS = [
	"Normal",
	"Fire",
	"Water",
	"Electric",
	"Grass",
	"Ice",
	"Fighting",
	"Poison",
	"Ground",
	"Flying",
	"Psychic",
	"Bug",
	"Rock",
	"Ghost",
	"Dragon",
	"Dark",
	"Steel",
	"Fairy"
]

NDEX = 0
NOME = -6
TIPO1 = -2
TIPO2 = -1
TIPO_NORMAL = 1
TIPO_FAIRY = -7

class RinhaDePokemon(MRJob):
	def steps(self):
		return [
			MRStep(mapper=self.mapperPorTipo, reducer=self.reducerCalculaEfetividade),
			MRStep(mapper=self.mapperOrdenaDano),
			MRStep(mapper=self.mapperGeraLista, reducer=self.reducerPokemonsEfetivos),
			MRStep(mapper=self.mapperFormatador)
		]

	def mapperPorTipo(self, _, linha):
		colunas = linha.split(",")

		if colunas[TIPO1] != "":
			if colunas[TIPO2] != "Unknown":
				yield colunas[TIPO1] + colunas[TIPO2], colunas
			else:
				yield colunas[TIPO2], colunas
	
	def reducerCalculaEfetividade(self, tipo, pokemons):
		dados = dict()
		listaPokemons = list(pokemons)
		dados["pokemons"] = listaPokemons
		dados["danos"] = []

		pokemon = listaPokemons[0]

		for indexA, damageA in enumerate(pokemon[TIPO_NORMAL:TIPO_FAIRY]):
			typeA = TIPOS[indexA]
			dados["danos"].append((typeA, float(damageA)))

			for indexB, damageB in enumerate(pokemon[TIPO_NORMAL:TIPO_FAIRY]):
				typeB = TIPOS[indexB]

				if typeA == typeB:
					continue

				dados["danos"].append((typeB, float(damageB)))
				dados["danos"].append((typeA + typeB, float(damageA) * float(damageB)))


		yield tipo, dados

	def mapperOrdenaDano(self, tipo, dado):
		dado["danos"].sort(key=lambda x:-x[1])
		yield tipo, dado

	def mapperGeraLista(self, tipo, dado):
		yield None, (tipo, dado)
	
	def reducerPokemonsEfetivos(self, _, dados):
		dadosPorTipo = dict([tuple(dado) for dado in list(dados)])

		for tipo, dado in dadosPorTipo.items():
			dado["pokemonsFortesContra"] = []
			for tipoDano, _ in dado["danos"]:
				if tipoDano in dadosPorTipo.keys():
					dado["pokemonsFortesContra"].extend(dadosPorTipo[tipoDano]["pokemons"])
			dado["pokemonsFortesContra"] = dado["pokemonsFortesContra"][0:10]

			yield tipo, dado

	def mapperFormatador(self, tipo, dado):
		for pokemon in dado["pokemons"]:
			formatado = {
				"name": pokemon[NOME],
				"tipo1": pokemon[TIPO1],
				"tipo2": pokemon[TIPO2],
				"pokemonsFortesContra": [{
					"ndex": pokemonForteContra[NDEX],
					"name": pokemonForteContra[NOME],
					"tipo1": pokemonForteContra[TIPO1],
					"tipo2": pokemonForteContra[TIPO2]
				} for pokemonForteContra in dado["pokemonsFortesContra"]]
			}

			yield pokemon[NDEX], formatado
	


if __name__ == '__main__':
	RinhaDePokemon.run()