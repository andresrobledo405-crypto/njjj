# Revisión del contenido de la biblioteca con GPT

El contenido de `app/library_data.txt` fue redactado por una IA a partir de conocimiento general. **Antes de usarlo con pacientes debe revisarlo un kinesiólogo.** GPT puede servir como primera revisión, pero también puede equivocarse: trate sus observaciones como sospechas por verificar en guías o literatura, no como verdad.

## Cómo usarlo
1. Abra ChatGPT y pegue el prompt de abajo.
2. Pegue el contenido de un archivo `parte_XX_*.txt` (uno por conversación o mensaje).
3. Guarde sus observaciones y entréguelas a quien mantiene KinePro para corregir el texto, o edite directamente la entrada en KinePro (Admin).

## Prompt
```
Eres un revisor clínico experto en kinesiología y fisioterapia (nivel posgrado).
A continuación hay entradas de una biblioteca educativa para kinesiólogos en Chile.
Para CADA entrada responde con una de estas etiquetas:
  OK            = correcta y razonablemente completa
  CORREGIR      = contiene un error o una afirmación imprecisa (cita la frase exacta y propón el texto corregido)
  ACTUALIZAR    = desactualizada respecto de guías o evidencia recientes (indica cuál)
  FALTA         = omite una precaución, contraindicación o bandera roja importante (indica cuál)
  DUDA          = no puedes verificarla con confianza
Reglas: no inventes citas ni cifras; si recuerdas una guía o estudio, nómbralo con cautela y marca "verificar".
No reescribas entradas que estén OK. Sé conciso. Termina con un resumen de los 5 hallazgos más importantes.
```

## Qué mirar con más atención
- Dosis, tiempos y cifras (series/repeticiones, grados de movilización, parámetros de electroterapia).
- Valores de corte de escalas (Berg, TUG, Tinetti, Tal, Ottawa).
- Contraindicaciones de agentes físicos y técnicas manuales.
- Contenido de kinesiología respiratoria pediátrica (bronquiolitis): siga siempre el protocolo local vigente.
