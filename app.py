
import streamlit as st
import pandas as pd
from io import BytesIO

st.title("Formulario de Pedido de Remeras")

st.subheader("Datos del cliente")
nombre = st.text_input("Nombre")
apellido = st.text_input("Apellido")
medio = st.selectbox("Medio de contacto", ["Instagram", "WhatsApp", "Otro"])
usuario = st.text_input("Usuario o teléfono")
mail = st.text_input("Correo electrónico")

st.subheader("Cantidad por talle")
talles_textiles = ['XS', 'S', 'M', 'L', 'XL', 'XXL']
talles_numericos = [str(i) for i in range(0, 18, 2)]
todos_talles = talles_textiles + talles_numericos

talles_cantidad = {}
cols = st.columns(6)
for i, talle in enumerate(todos_talles):
    with cols[i % 6]:
        cantidad = st.number_input(f"{talle}", min_value=0, max_value=20, step=1)
        if cantidad > 0:
            talles_cantidad[talle] = cantidad

campos_formulario_2 = []
if talles_cantidad:
    st.subheader("Detalle por prenda")

    for talle, cantidad in talles_cantidad.items():
        for i in range(cantidad):
            st.markdown(f"**Talle {talle} – Prenda {i+1}**")
            col1, col2 = st.columns([2, 3])
            with col1:
                persona = st.text_input(f"¿Para quién es? (Talle {talle}, prenda {i+1})", key=f"persona_{talle}_{i}")
            with col2:
                ubicacion = st.multiselect(
                    "Ubicación de estampa",
                    ["pecho", "espalda", "manga"],
                    key=f"ubicacion_{talle}_{i}"
                )
            campos_formulario_2.append((talle, persona, ubicacion))

if campos_formulario_2 and st.button("Generar y descargar Excel"):
    errores = []
    datos = []

    for i, (talle, persona, ubicacion) in enumerate(campos_formulario_2, 1):
        if not persona.strip() or not ubicacion:
            errores.append(f"Fila {i}: faltan datos (Nombre o ubicación)")
        datos.append({
            "Talle": talle,
            "Persona": persona.strip(),
            "Ubicación": ", ".join(ubicacion)
        })

    if errores:
        st.error("No se puede generar el archivo. Corregí los siguientes errores:")
        for e in errores:
            st.write(f"- {e}")
    else:
        df_pedido = pd.DataFrame(datos)
        df_cliente = pd.DataFrame([{
            "Nombre": nombre.strip(),
            "Apellido": apellido.strip(),
            "Medio": medio,
            "Usuario": usuario.strip(),
            "Mail": mail.strip()
        }])

        conteo_por_talle = df_pedido["Talle"].value_counts().sort_index()
        df_resumen = conteo_por_talle.reset_index()
        df_resumen.columns = ["Talle", "Cantidad"]
        total = pd.DataFrame([{"Talle": "TOTAL", "Cantidad": df_resumen["Cantidad"].sum()}])
        df_resumen = pd.concat([df_resumen, total], ignore_index=True)

        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_cliente.to_excel(writer, sheet_name="datos_cliente", index=False)
            df_resumen.to_excel(writer, sheet_name="resumen_pedido", index=False)
            df_pedido.to_excel(writer, sheet_name="datos_pedido", index=False)
        output.seek(0)

        st.success("Archivo generado con éxito.")
        st.download_button(
            label="Descargar Excel",
            data=output,
            file_name="pedido_personalizado.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )