
import gpt_2_simple as gpt2

# Descargar el modelo GPT-2 (solo necesario la primera vez)
gpt2.download_gpt2(model_name="124M")

# Cargar el modelo preentrenado
sess = gpt2.start_tf_sess()
gpt2.load_gpt2(sess, model_name="124M")

# Generar texto
prompt = "Escribe un párrafo sobre una chica llamada antonia, en su cuarto."
gen_text = gpt2.generate(sess, model_name="124M", prefix=prompt, length=150, temperature=0.7, return_as_list=True)[0]

print("Texto generado:")
print(gen_text)
