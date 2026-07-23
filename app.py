import streamlit as st
import json
import pandas as pd
from google import genai

st.set_page_config(
    page_title="Extrator Pro do Google Maps",
    page_icon="📍",
    layout="wide"
)

st.title("📍 Extrator Pro de Dados do Google Maps")
st.write("Processe listas individuais ou grandes volumes de dados e baixe direto em Excel/CSV.")

SYSTEM_PROMPT = """
<agent_system_prompt>
  <role>
    <name>Agente de Extração de Dados do Google Maps</name>
    <objective>Extrair todos os dados comerciais e retornar EXCLUSIVAMENTE uma lista de objetos em JSON válido.</objective>
  </role>
  <directives>
    <rule id="1">Retorne estritamente um Array JSON de objetos com as empresas encontradas.</rule>
    <rule id="2">Não inclua texto explicativo fora do JSON.</rule>
  </directives>
  <output_schema>
    <format>JSON Array</format>
    <structure>
      [
        {
          "nome_empresa": "String | null",
          "categoria": "String | null",
          "telefone_fixo": "String | null",
          "whatsapp": "String | null",
          "email": "String | null",
          "website": "String | null",
          "endereco_completo": "String | null",
          "cidade": "String | null",
          "estado": "String | null",
          "horario_funcionamento": "String | null",
          "nota_avaliacao": "Number | null",
          "total_avaliacoes": "Integer | null"
        }
      ]
    </structure>
  </output_schema>
</agent_system_prompt>
"""

# Barra Lateral
api_key = st.sidebar.text_input("API Key do Google Gemini:", type="password")

st.sidebar.markdown("---")
st.sidebar.subheader("📂 Opção de Entrada por Arquivo")
uploaded_file = st.sidebar.file_uploader("Envie um arquivo .txt com a lista de empresas", type=["txt"])

# Entrada por texto manual
input_text = st.text_area(
    "Ou cole aqui o texto bruto copiado do Google Maps:",
    height=200,
    placeholder="Cole os dados das empresas aqui..."
)

# Define o texto final
final_text = ""
if uploaded_file is not None:
    final_text = uploaded_file.read().decode("utf-8")
elif input_text.strip():
    final_text = input_text

if st.button("🚀 Extrair, Organizar e Gerar Planilha", type="primary"):
    if not api_key:
        st.error("⚠️ Insira sua API Key do Google Gemini na barra lateral.")
    elif not final_text.strip():
        st.warning("⚠️ Cole o texto ou faça upload de um arquivo .txt.")
    else:
        with st.spinner("Processando e estruturando os dados..."):
            try:
                client = genai.Client(api_key=api_key)
                
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=f"{SYSTEM_PROMPT}\n\n[INPUT_STATE]\n{final_text}"
                )
                
                # Trata a resposta para ler como JSON
                clean_json = response.text.replace("```json", "").replace("```", "").strip()
                data = json.loads(clean_json)
                
                st.success("✅ Extração concluída!")
                
                # Cria DataFrame no Pandas
                df = pd.DataFrame(data)
                
                st.subheader("📊 Tabela de Resultados")
                st.dataframe(df, use_container_width=True)
                
                # Botões de Download
                col1, col2 = st.columns(2)
                
                csv = df.to_csv(index=False).encode('utf-8')
                col1.download_button(
                    label="📥 Baixar em CSV (Excel)",
                    data=csv,
                    file_name='empresas_google_maps.csv',
                    mime='text/csv',
                )
                
                col2.download_button(
                    label="📋 Baixar em JSON",
                    data=clean_json,
                    file_name='empresas_google_maps.json',
                    mime='application/json',
                )
                
            except Exception as e:
                st.error(f"❌ Erro ao processar os dados: {e}")
                st.info("Dica: Certifique-se de que o retorno veio formatado como JSON válido.")
