# thcode-ProjSSTMap

Esse é o primeiro conjunto de codigos da tese. É responsável pela geração de mapas.

Fazem parte desse codigo:

Nmain.py : programa principal que chama a classe principal "GenerateMaps" dentro do codigo "NGenerateMaps.py.

NGenerateMaps.py : Lê todos os arquivos de entrada (mapas) e inicia a reparação de todos.

MapRepair.py : Utiliza a técnica de comparação criada pelo Jorge Ferenando para corrigir o Mapa.

ArtificialMap.py : Classe que gera o mapa artificial para comparação.

SSTMap.py : Classe que gerencia a leitura dos Mapas oriundos da classe SSTMethods.py

SSTMethods.py : O arquivo sst_methods.py que foi transformado em Classe.

PlotMap.py : gera mapas em arquivos (.png). Poder gerar figuras contendo 6 mapas (1 para cada canal do SST) ou mapas separados independentemente de canal.

Conforme combinamos, o que precisa ser feito:

1.Mudar os parâmetros para o formato do linux.
AS-IS EX:
ATHBPOS='C:\\dadosSST\\beans\\bpos.save'
PATHSTBEAMS='C:\\dadosSST\\beans\\stackedbeams2012.txt'

estão nos arquivos iniciais Nmain, GenerateMaps e MapRepair

2. Entender e documentar cada modulo.

3. Atualizar o programa para Python 3 e alterar o programa de acesso aos dados do SST que o Guigue fez.

Assim que for entendendo e executando, você pode melhorar o codigo. É o tempo que organizo para colocar os programas seguintes.

OBS: O arquivo "M06 - Copy.7z" contem uma amostra de binários e o arquivo "SST_maps.zip" contem os mapas gerados através dos binarios. 

