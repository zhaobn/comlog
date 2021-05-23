const defaultStone = { 'borderWidth': '8px', 'mar': 5, 'len': 60 };
const smallStone = { 'borderWidth': '3px', 'mar': 3, 'len': 20 };

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
  parentDiv.append(createAgentStone(`learn${config.trial}-agent`, config.agent));
  parentDiv.append(createBlocks(`learn${config.trial}-recipient`, config));
  return(parentDiv);
}
function createInitHistory(config, parentDiv) {
  let textDiv = createCustomElement('div', 'hist-text', id=`learn${config.trial}-hist-text`)
  textDiv.append(createText('h2', 'Before'))
  parentDiv.append(textDiv);
  parentDiv.append(createBlocks(`learn${config.trial}-recipient`, config));
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
  let div = createCustomElement("div", "recipient-stone-div", `${id}-blocks-all`);
  let length = stoneOpts.recipient % 10
  let max =  stoneOpts.result % 10
  for(let i = 0; i < max; i++ ) {
    let block = createCustomElement("div", "recipient-block", `${id}-block-${i}`)
    block.style.opacity = (i < length)? 1: 0
    div.append(block)
  }
  return(div);
}

function createRecipientStone(id, stoneOpts) {
  let div = document.getElementById(`${id}-blocks-all`)
  let length = stoneOpts % 10;
  for(let i = 0; i < length; i++ ) {
    div.append(createCustomElement("div", "recipient-block", `${id}-block-${i+1}`))
  }
  return(div);
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
function playEffects (config) {
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
  const agent = `learn${config.trial}-agent-div`;
  const recipient = `learn${config.trial}-recipient-blocks-all`;

  const agentStone = document.getElementById(agent);
  const startPos = getCurrentLocation(agent).right;
  const endPos = getCurrentLocation(recipient).left;

  const delta = Math.round(endPos - startPos) + 15;
  (delta > 0) && (agentStone.style.left = `${delta}px`);

  setTimeout(() => {
    let initLen = config.recipient % 10
    let targetLen = config.result % 10
    let hist = document.getElementById(`task-obs-training-displayhist-${config.trial}`)
    for (let i = initLen; i < targetLen; i++ ) {
      fadeIn(document.getElementById(`learn${config.trial}-recipient-block-${i}`))
      setTimeout(()=> hist.style.opacity = 1, 1000)
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
