-- Estúdio Bíblico: renderiza o quadro atual em PNG, ao lado do arquivo .moho aberto.
-- Instalação: copiar para <pasta de conteúdo do Moho>\Scripts\Menu\Estudio\ e reabrir o Moho.
-- Uso: menu Scripts > Estudio > Renderizar quadro (PNG).

ScriptName = "ES_RenderizarQuadro"

ES_RenderizarQuadro = {}

function ES_RenderizarQuadro:Name() return "Renderizar quadro (PNG)" end
function ES_RenderizarQuadro:Version() return "1.0" end
function ES_RenderizarQuadro:Description() return "Salva o quadro atual como PNG ao lado do arquivo .moho" end
function ES_RenderizarQuadro:Creator() return "Estudio Biblico" end
function ES_RenderizarQuadro:UILabel() return "Renderizar quadro (PNG)" end

function ES_RenderizarQuadro:Run(moho)
	local doc = moho.document:Path()
	if doc == nil or doc == "" then
		LM.GUI.Alert(LM.GUI.ALERT_WARNING, "Salve o arquivo .moho antes de renderizar.", nil, nil, "OK", nil, nil)
		return
	end
	local saida = string.gsub(doc, "%.moho$", "") .. "_render_moho_q" .. moho.frame .. ".png"
	local ok, erro = pcall(function() moho:FileRender(saida) end)
	if ok then
		print("Render salvo em: " .. saida)
		LM.GUI.Alert(LM.GUI.ALERT_INFO, "Render salvo em:", saida, nil, "OK", nil, nil)
	else
		print("Falha no render: " .. tostring(erro))
		LM.GUI.Alert(LM.GUI.ALERT_WARNING, "Falha no render:", tostring(erro), nil, "OK", nil, nil)
	end
end
