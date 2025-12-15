import streamlit as st
from pypdf import PdfReader, PdfWriter
import zipfile
import io
import os

# Configuración de la página
st.set_page_config(
    page_title="PDF Splitter Pro",
    page_icon="📄",
    layout="centered"
)

def procesar_pdf_en_memoria(archivo_upload):
    """
    Recibe un archivo subido, separa las páginas y retorna un objeto BytesIO
    que contiene un archivo ZIP con todas las páginas.
    """
    # Buffer en memoria para el ZIP final
    zip_buffer = io.BytesIO()
    
    try:
        reader = PdfReader(archivo_upload)
        nombre_original = os.path.splitext(archivo_upload.name)[0]
        
        # Barra de progreso para UX
        progress_text = "Procesando páginas..."
        my_bar = st.progress(0, text=progress_text)
        total_paginas = len(reader.pages)

        # Creamos el ZIP en memoria
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for i, page in enumerate(reader.pages):
                writer = PdfWriter()
                writer.add_page(page)
                
                # Creamos un buffer temporal para ESTA página específica
                pdf_bytes = io.BytesIO()
                writer.write(pdf_bytes)
                
                # Definimos el nombre del archivo dentro del ZIP
                nombre_salida = f"{nombre_original}_pag{i + 1}.pdf"
                
                # Escribimos los bytes en el ZIP
                zf.writestr(nombre_salida, pdf_bytes.getvalue())
                
                # Actualizar barra de progreso
                my_bar.progress((i + 1) / total_paginas, text=f"Separando página {i+1} de {total_paginas}")

        my_bar.empty() # Limpiar barra al terminar
        zip_buffer.seek(0) # Rebobinar el puntero al inicio del archivo
        return zip_buffer, total_paginas

    except Exception as e:
        st.error(f"Ocurrió un error al procesar el PDF: {e}")
        return None, 0

# --- INTERFAZ DE USUARIO (Frontend) ---

st.title("📄 Separador de PDF Web")
st.markdown("""
Sube tu archivo PDF y obtén un **ZIP** con todas las páginas separadas al instante.
*Procesado en memoria RAM para máxima velocidad.*
""")

uploaded_file = st.file_uploader("Arrastra tu PDF aquí", type="pdf")

if uploaded_file is not None:
    # Verificamos si tiene páginas (por si acaso es un archivo corrupto)
    try:
        # Botón de acción
        if st.button("✂️ Separar Páginas", type="primary"):
            with st.spinner('Trabajando en tu archivo...'):
                zip_resultado, num_paginas = procesar_pdf_en_memoria(uploaded_file)
            
            if zip_resultado:
                st.success(f"¡Listo! Se extrajeron {num_paginas} páginas.")
                
                # Botón de descarga
                st.download_button(
                    label="⬇️ Descargar Archivos (ZIP)",
                    data=zip_resultado,
                    file_name=f"paginas_separadas.zip",
                    mime="application/zip"
                )
    except Exception as e:
        st.error("El archivo parece estar dañado o encriptado.")

# Footer simple
st.markdown("---")
st.caption("Desarrollado con Python y Streamlit")