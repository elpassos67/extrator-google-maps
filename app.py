import streamlit as st
from google import genai

# Configuração da página do Streamlit
st.set_page_config(
    page_title="Extrator de Dados do Google Maps",
    page_icon="📍",
    layout="wide"
)

st.title("📍 Extrator de Dados do Google Maps")
st.write("Cole o texto bruto copiado do Google Maps para estruturar todas as informações comercialmente.")

# Prompt do Sistema (Kernel de Extração do Google Maps)
SYSTEM_PROMPT = """
<agent_system_prompt>
  <role>
    <name>Agente de Extração de Dados do Google Maps</name>
    <objective>Extrair todos os dados comerciais do texto fornecido e retornar em formato JSON estrito.</objective>
  </role>
  <directives>
    <rule id="1">Extrair: Nome, Categoria, Telefone, WhatsApp, E-mail, Website, Endereço Completo, Horários, Nota e Avaliações.</rule>
    <rule id="2">Se o dado não existir no texto, definir como null.</rule>
  </directives>
  <output_schema>
    <format>JSON</format>
    <structure>
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
    </structure>
  </output_schema>
</agent_system_prompt>
"""

# Campo para inserir a chave de API do Gemini
api_key = st.sidebar.text_input("Insira sua API Key do Google Gemini:", type="password")

# Campo principal de entrada de texto
input_text = st.text_area(
    "Cole aqui o texto bruto copiado do Google Maps:",
    height=250,
    placeholder="Exemplo: Empresa X - Rua ABC, 123 - Tel: (11) 99999-9999..."
)

if st.button("🚀 Extrair e Organizar Dados", type="primary"):
    if not api_key:
        st.error("⚠️ Por favor, insira sua chave da API do Google Gemini na barra lateral esquerda.")
    elif not input_text.strip():
        st.warning("⚠️ Cole algum texto no campo antes de clicar no botão.")
    else:
        with st.spinner("Processando e estruturando os dados..."):
            try:
                # Inicializa o cliente do Gemini
                client = genai.Client(api_key=api_key)
                
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=f"{SYSTEM_PROMPT}\n\n[INPUT_STATE]\n{input_text}"
                )
                
                st.success("✅ Extração concluída com sucesso!")
                
                # Exibição do resultado
                st.subheader("📊 Resultado Estruturado")
                st.code(response.text, language="json")
                
            except Exception as e:
                st.error(f"❌ Ocorreu um erro durante o processamento: {e}")
