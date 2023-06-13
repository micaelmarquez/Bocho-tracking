# Bocho-tracking-Biomedical-Engineer-Final-Project

Headmouse for users with a severe motor impairment, using computer vision and data management libraries from Python.

Introducción
-------------------------
En la Argentina, debido al elevado costo de importación de dispositivos de accesibilidad y a la limitada cantidad de opciones (nacionales y extranjeras), el acceso a los HID 
(Human Interface Device, dispositivo de interfaz humana en español) es cada vez más reducido. Esta limitación afecta, entre otros, a personas con tetraplejia y en ellos provoca
dificultad en el acceso a información actualizada, comunicación a distancia, trabajo y recreación.

Debido a las opciones limitadas y a los elevados costos de importación, las empresas dedicadas a brindar accesibilidad a dichas personas (y sus familias también) terminan 
optando por soluciones que no implican un costo alguno, y si bien no son malas, muchas veces la accesibilidad no es la óptima, provocando frustración, lentitud para 
realizar tareas e incluso puede llegar a generar rechazo en el uso de las tecnologías de accesibilidad.


Esta situación me motivó a desarrollar un prototipo funcional para la empresa OTTAA Project, que solucione el problema planteado. 
Se abordó la problemática realizando un análisis de usuarios en situación de dicha discapacidad, donde se evaluaron sus habilidades motrices y cognitivas. Luego, se propuso 
realizar un análisis de usuarios y una encuesta a los mismos, con el fin de entender qué es lo que buscan en este tipo de dispositivos. A continuación, se realizó un 
análisis de tecnologías actuales que son capaces de satisfacer la necesidad planteada previamente y se elige una tecnología para desarrollar. Finalmente, se definen 
requerimientos de usabilidad y funcionalidad del dispositivo. 

El código fue desarrollado en Python, a fin de implementar y realizar pruebas, y se implementó un primer prototipo del HID. 

El presente trabajo tuvo como fin el desarrollo de un dispositivo de accesibilidad a la computadora para personas cuya movilidad es reducida desde el cuello hacia abajo, 
independientemente de la lesión o patología que posean. 

RESULTADOS
-------------------------
El dispositivo desarrollado, llamado y registrado como Bocho \textregistered, es una alternativa para controlar el cursor de la computadora mediante movimientos cefálicos 
simples, y lo más importante, de forma autónoma. Funciona mediante luz infrarroja, la cual emitida por un arreglo de LEDs infrarrojos, que luego es reflejada por un sticker 
reflectante que posee el usuario en un par de anteojos simples, o bien sobre su piel. Parte de la luz reflejada por el sticker reflectante llega a una cámara web, donde 
se encuentra un filtro de luz visible que elimina todo el espectro electromagnético correspondiente al rango visible.

Este sistema es significativamente más barato a las alternativas actuales en el mercado y además cuenta con una precisión más alta, que permite utilizar incluso aplicaciones 
de diseño y modelado.

Palabras Clave
-------------------------
dispositivo de accesibilidad, diseño y desarrollo, tetraplejia, python, computer vision.
