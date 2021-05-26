const defaultStone = { 'borderWidth': '8px', 'mar': 5, 'len': 60 };
const smallStone = { 'borderWidth': '3px', 'mar': 3, 'len': 20 };
const maxBlocks = 8

function createCustomElement (type = 'div', className, id) {
  let element = (["svg", "polygon"].indexOf(type) < 0)?
    document.createElement(type):
    document.createElementNS("http://www.w3.org/2000/svg", type);
  if (className.length > 0) element.setAttribute("class", className);
  element.setAttribute("id", id);
  return element;
}
function createDivWithStyle (className = "div", id = "", style = "") {
  let element = createCustomElement('div', className, id);
  setStyle(element, style);
  return element;
}
function createText(h = "h1", text = 'hello') {
  let element = document.createElement(h);
  let tx = document.createTextNode(text);
  element.append(tx);
  return(element)
}
function setAttributes(el, attrs) {
  for(var key in attrs) {
    el.setAttribute(key, attrs[key]);
  }
}
function createBtn (btnId, text = "Button", on = true, className = "task-button") {
  let btn = createCustomElement("button", className, btnId);
  btn.disabled = !on;
  (text.length > 0) ? btn.append(document.createTextNode(text)): null;
  return(btn)
}
function createInitStones(config, parentDiv) {
  let spaceDiv = createCustomElement("div", "display-main-space", `${learnDivPrefix}-displaymainspace-${config.trial}`)
  let agentDiv = createCustomElement("div", "display-main-agent", `${learnDivPrefix}-displaymainagent-${config.trial}`)
  let recipientDiv = createCustomElement("div", "display-main-recipient", `${learnDivPrefix}-displaymainrecipient-${config.trial}`)
  agentDiv.append(createAgentStone(`learn${config.trial}-agent`, config.agent))
  recipientDiv.append(createBlocks(`learn${config.trial}-recipient`, config))
  parentDiv.append(spaceDiv)
  parentDiv.append(agentDiv)
  parentDiv.append(recipientDiv)
  return(parentDiv);
}
function createInitHistory(config, parentDiv) {
  let spaceDiv = createCustomElement("div", "display-main-space", `${learnDivPrefix}-displaymainspace-hist-${config.trial}`)
  let agentDiv = createCustomElement("div", "display-main-agent", `${learnDivPrefix}-displaymainagent-hist-${config.trial}`)
  let recipientDiv = createCustomElement("div", "display-main-recipient", `${learnDivPrefix}-displaymainrecipient-hist-${config.trial}`)

  let textDiv = createCustomElement('div', 'hist-text', id=`learn${config.trial}-hist-text`)
  textDiv.append(createText('h2', 'Before'))
  spaceDiv.append(textDiv);
  agentDiv.append(createAgentStone(`learn${config.trial}-hist-agent`, config.agent))
  recipientDiv.append(createBlocks(`learn${config.trial}-hist-recipient`, config))

  parentDiv.append(spaceDiv)
  parentDiv.append(agentDiv)
  parentDiv.append(recipientDiv)
  return(parentDiv);
}
function createAgentStone(id, stoneOpts) {
  let div = createCustomElement("div", "agent-stone-div", `${id}-div`);
  let svg = createCustomElement("svg", "stone-svg", `${id}-svg`);
  svg.append(createPolygon('agent-stone', `${id}`, Math.floor(stoneOpts/10), 'default'))
  div.append(svg)
  return(div);
}
function createBlocks(id, stoneOpts=0) {
  let isGenTask = id.substring(0,3)==='gen'
  let div = createCustomElement("div", "recipient-stone-div", `${id}-blocks-all`);
  let length = stoneOpts.recipient % 10
  let max =  stoneOpts.result % 10 || maxBlocks
  for(let i = 0; i < max; i++ ) {
    let block = createCustomElement("div", "recipient-block", `${id}-block-${i}`)
    block.style.opacity = (i < length)? 1 : (isGenTask==0)? 0 : blockOpDecay(i, length)
    div.append(block)
  }
  return(div);
}
function createGenStones(config, parentDiv) {
  let spaceDiv = createCustomElement("div", "display-main-space", `gen${config.trial}-display-space-div`)
  let agentDiv = createCustomElement("div", "display-main-agent", `gen${config.trial}-display-agent-div`)
  let recipientDiv = createCustomElement("div", "display-main-recipient", `gen${config.trial}-display-recipient-div`)

  agentDiv.append(createAgentStone(`gen${config.trial}-agent`, config.agent));
  recipientDiv.append(createBlocks(`gen${config.trial}-recipient`, config));

  parentDiv.append(spaceDiv)
  parentDiv.append(agentDiv)
  parentDiv.append(recipientDiv)
  return(parentDiv);
}
function blockOpDecay(index, base) {
  return 0.1 - 0.01*(index - base)
}

function genBlocksEffects(config) {
  for(let i = 0; i < maxBlocks; i++ ) {
    let idPrefix = `gen${config.trial}-recipient-block-`
    let base = config.recipient % 10
    document.getElementById(`${idPrefix}${i}`).onmousemove = () => highlightBlocksOnMouseOver(idPrefix, i, base)
    document.getElementById(`${idPrefix}${i}`).onmouseout = () => highlightBlocksOnClick(idPrefix, i, base)
    document.getElementById(`${idPrefix}${i}`).onclick = () => highlightBlocksOnClick(idPrefix, i, base)
  }
}
function handleGenSelection(config) {
  let blocksDiv = document.getElementById(`gen${config.trial}-recipient-blocks-all`)
  let resetBtn = document.getElementById(`task-gen-reset-btn-${config.trial}`)
  let confirmBtn = document.getElementById(`task-gen-confirm-btn-${config.trial}`)
  blocksDiv.onclick = () => {
    resetBtn.disabled = false
    confirmBtn.disabled = false
  }
}

function highlightBlocksOnMouseOver(idPrefix, i, base) {
  let baseBlocks = Array.from(Array(base).keys()).map(m => `${idPrefix}${m}`)
  let yesBlocks = Array.from(Array(maxBlocks).keys()).filter(b => (b>=base && b <= i)).map(m => `${idPrefix}${m}`)
  let noBlocks = Array.from(Array(maxBlocks).keys()).filter(b => b > i).map(m => `${idPrefix}${m}`)
  baseBlocks.forEach(b => document.getElementById(b).style.opacity=1)
  yesBlocks.forEach(b => document.getElementById(b).style.opacity=0.5)
  noBlocks.forEach(b => document.getElementById(b).style.opacity=blockOpDecay(parseInt(b.split('-')[3]), base))
}
function highlightBlocksOnClick(idPrefix, i, base) {
  let yesBlocks = Array.from(Array(maxBlocks).keys()).map(m => `${idPrefix}${m}`)
  let noBlocks = Array.from(Array(maxBlocks).keys()).filter(b => b > i).map(m => `${idPrefix}${m}`)
  yesBlocks.forEach(b => document.getElementById(b).style.opacity=1)
  noBlocks.forEach(b => document.getElementById(b).style.opacity=blockOpDecay(parseInt(b.split('-')[3]), base))
}
function resetGenBlock(config) {
  let length = config.recipient % 10
  for(let i = 0; i < maxBlocks; i++ ) {
    let block = document.getElementById(`gen${config.trial}-recipient-block-${i}`)
    block.style.opacity = (i < length)? 1 : blockOpDecay(i, length)
  }
}

function createPolygon(className, id, sides, scale) {
  let polygon = createCustomElement("polygon", className, id);

  n = parseInt(sides);
  let output = [];
  let adjust = (n===5)? 55 : 0;

  let mar = (scale==='default')? defaultStone.mar: smallStone.mar;
  let len = (scale==='default')? defaultStone.len: smallStone.len;

  if (n === 3) {
    output.push(`${len/2},${mar}`);
    output.push(`${len-mar},${len-mar}`);
    output.push(`${mar},${len-mar}`);
  } else if (n === 4) {
    output.push(`${mar},${mar}`);
    output.push(`${len-mar},${mar}`);
    output.push(`${len-mar},${len-mar}`);
    output.push(`${mar},${len-mar}`);
  } else {
    // Adapted from https://gist.github.com/jonthesquirrel/e2807811d58a6627ded4
    for (let i = 1; i <= n; i++) {
      output.push(
        ((len/2 * Math.cos(adjust + 2 * i * Math.PI / n)) + len/2).toFixed(0).toString() + "," +
        ((len/2 * Math.sin(adjust + 2 * i * Math.PI / n)) + len/2).toFixed(0).toString()
      )
    }
  }
  setAttributes(polygon, { "points": output.join(" ") });
  return(polygon);
}
function clearElement (id) {
  let clear = document.getElementById(id);
  clear.remove();
}
function playEffects (config, clicked=0) {
  const getCurrentLocation = (id) => {
    let rect = {top: 0, bottom: 0, left: 0, right: 0};
    const pos = document.getElementById(id).getBoundingClientRect();
    rect.top = pos.top;
    rect.bottom = pos.bottom;
    rect.left = pos.left;
    rect.right = pos.right;
    return rect;
  }

  if (!(document.body.contains(document.getElementById(`learn${config.trial}-agent-div`)))) {
    createStones(config)
  }

  const agentStone = document.getElementById(`learn${config.trial}-agent-div`);
  const startPos = getCurrentLocation(`learn${config.trial}-agent`).right;
  const endPos = getCurrentLocation(`learn${config.trial}-recipient-blocks-all`).left;

  const delta = Math.round(endPos - startPos);
  (delta > 0) && (agentStone.style.left = `${delta}px`);

  setTimeout(() => {
    let initLen = config.recipient % 10
    let targetLen = config.result % 10
    let hist = document.getElementById(`task-training-displayhist-${config.trial}`)
    for (let i = initLen; i < targetLen; i++ ) {
      fadeIn(document.getElementById(`learn${config.trial}-recipient-block-${i}`))
      if (clicked == 0) {
        setTimeout(()=> {
          hist.style.opacity = 0
          hist.style.display = 'flex'
          fadeIn(hist)
        }, 1000)
      }
    }
  }, 1500);
}


function fadeIn(element) {
  let op = 0.1;
  let timer = setInterval(() => {
    if (op >= 1) {
        clearInterval(timer);
    }
    element.style.opacity = op;
    element.style.filter = 'alpha(opacity=' + op * 100 + ")";
    op += op * 0.1;
  }, 20);
}
function showNext(id, display = "flex") {
  let div = document.getElementById(id);
  div.style.display = display;
  div.scrollIntoView(true);
}
function hide(id) {
  let div = document.getElementById(id);
  div.style.display = "none";
}
function createPretrainings(parentDiv) {
  for(let i = 0; i < 3; i++ ) {
    let obsId = i + 1
    let div = createCustomElement('div', 'detect-div', `pretrain-detect-div-${obsId}`)
    let agent = createCustomElement('div', 'detect-div-agent', `pretrain-detect-div-agent-${obsId}`)
    agent.append(createAgentStone(`pretrain-detect-agent-${obsId}`, (i+3)*10+1))
    let power = createCustomElement('div', 'detect-div-power', `pretrain-detect-div-power-${obsId}`)
    power.innerHTML = `<p>${'&#9733;'.repeat(i+1)}</p>`
    div.append(agent)
    div.append(power)
    parentDiv.append(div)
  }
  return parentDiv
}
