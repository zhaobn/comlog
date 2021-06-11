const defaultStone = { 'borderWidth': '8px', 'mar': 5, 'len': 60 };
const smallStone = { 'borderWidth': '3px', 'mar': 3, 'len': 20 };
const maxBlocks = 12

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
// function createAgentStone(id, stoneOpts) {
//   let div = createCustomElement("div", "agent-stone-div", `${id}-div`);
//   let svg = createCustomElement("svg", "stone-svg", `${id}-svg`);
//   svg.append(createPolygon('agent-stone', `${id}`, Math.floor(stoneOpts/10), 'default'))
//   div.append(svg)
//   return(div);
// }
function createAgentStone(id, nStripes = 1, base = 40, r = 25) {
  nStripes = Math.floor(nStripes/10)
  const getDelta = (x) => (-x + Math.sqrt(2*(r**2)-x**2))/2

  let agentDiv = createCustomElement("div", "agent-stone-div", `${id}-div`);
  let agentStoneSvg = createCustomElement('svg', 'stone-svg', id)
  let circleSvg = '<circle class="agent-stone" cx="40" cy="40" r="30" />'
  let stripes = ''

  switch (nStripes) {
    case 1:
      stripes = `<line class="agent-stone-stripe" x1="${base+getDelta(0)}" y1="${base-getDelta(0)}" x2="${base-getDelta(0)}" y2="${base+getDelta(0)}" />`;
      break;
    case 2:
      stripes = `<line class="agent-stone-stripe" x1="${base+getDelta(15)}" y1="${base-getDelta(15)-15}" x2="${base-getDelta(15)-15}" y2="${base+getDelta(15)}" />` + '\n' +
      `<line class="agent-stone-stripe" x1="${base+getDelta(15)+15}" y1="${base-getDelta(15)}" x2="${base-getDelta(15)}" y2="${base+getDelta(15)+15}" />`
      break;
    case 3:
      stripes = `<line class="agent-stone-stripe" x1="${base+getDelta(0)}" y1="${base-getDelta(0)}" x2="${base-getDelta(0)}" y2="${base+getDelta(0)}" />` + '\n' +
      `<line class="agent-stone-stripe" x1="${base+getDelta(20)}" y1="${base-getDelta(20)-20}" x2="${base-getDelta(20)-20}" y2="${base+getDelta(20)}" />` + '\n' +
      `<line class="agent-stone-stripe" x1="${base+getDelta(20)+20}" y1="${base-getDelta(20)}" x2="${base-getDelta(20)}" y2="${base+getDelta(20)+20}" />`
      break;
    case 4:
      stripes = `<line class="agent-stone-stripe" x1="${base+getDelta(8)}" y1="${base-getDelta(8)-8}" x2="${base-getDelta(8)-8}" y2="${base+getDelta(8)}" />` + '\n' +
      `<line class="agent-stone-stripe" x1="${base+getDelta(8)+8}" y1="${base-getDelta(8)}" x2="${base-getDelta(8)}" y2="${base+getDelta(8)+8}" />` + '\n' +
      `<line class="agent-stone-stripe" x1="${base+getDelta(25)}" y1="${base-getDelta(25)-25}" x2="${base-getDelta(25)-25}" y2="${base+getDelta(25)}" />` + '\n' +
      `<line class="agent-stone-stripe" x1="${base+getDelta(25)+25}" y1="${base-getDelta(25)}" x2="${base-getDelta(25)}" y2="${base+getDelta(25)+25}" />`
      break;
  }
  agentStoneSvg.innerHTML = circleSvg + stripes
  agentDiv.append(agentStoneSvg)
  return agentDiv
}
function createBlocks(id, stoneOpts) {
  let div = createCustomElement("div", "recipient-stone-div", `${id}-blocks-all`);
  let length = stoneOpts.recipient % 10
  let max =  (stoneOpts.task_phase=='gen')? maxBlocks: stoneOpts.result % 10
  for(let i = 0; i < max; i++ ) {
    let block = createCustomElement("div", "recipient-block", `${id}-block-${i}`)
    block.style.opacity = (i < length)? 1 : (stoneOpts.task_phase=='gen')? blockOpDecay(i, length) : 0
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
  return (index > base + 1)? 0: 0.1 - 0.001*(index - base)
}

function genBlocksEffects(config, genClicked) {
  for(let i = 0; i < maxBlocks; i++ ) {
    let idPrefix = `gen${config.trial}-recipient-block-`
    let base = config.recipient % 10
    let blockDiv = document.getElementById(`${idPrefix}${i}`)
    blockDiv.onmousemove = () => highlightBlocksOnMouseOver(idPrefix, i, base)
    blockDiv.onmouseout = () => highlightBlocks(idPrefix, i, base)
    blockDiv.onclick = () => {
      highlightBlocks(idPrefix, i, base)
      if (genClicked[config.trial-1] % 2 == 1) {
        for(let i = 0; i < maxBlocks; i++ ) {
          let blockDiv = document.getElementById(`${idPrefix}${i}`)
          blockDiv.onmousemove = () => highlightBlocksOnMouseOver(idPrefix, i, base)
          blockDiv.onmouseout = () => highlightBlocks(idPrefix, i, base)
        }
      } else {
        for(let i = 0; i < maxBlocks; i++ ) {
          let blockDiv = document.getElementById(`${idPrefix}${i}`)
          blockDiv.onmousemove = () => null
          blockDiv.onmouseout = () => null
        }
      }
      genClicked[config.trial-1] += 1
    }
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
function getCurrentSelection(config) {
  let blocksDiv = document.getElementById(`gen${config.trial}-recipient-blocks-all`)
  let blockOps = []
  for(let i = 0; i < maxBlocks; i++ ) {
    blockOps.push(document.getElementById(`gen${config.trial}-recipient-block-${i}`).style.opacity)
  }
  return(findAllIndex('1',blockOps).length)
}
function disableBlocks(config) {
  document.getElementById(`gen${config.trial}-recipient-blocks-all`).onclick = null
  for(let i = 0; i < maxBlocks; i++ ) {
    let blockDiv = document.getElementById(`gen${config.trial}-recipient-block-${i}`)
    blockDiv.onmousemove = () => null
    blockDiv.onmouseout = () => null
    blockDiv.onclick = () => null
  }
}
function highlightBlocksOnMouseOver(idPrefix, i, base) {
  let baseBlocks = Array.from(Array(base).keys()).map(m => `${idPrefix}${m}`)
  let yesBlocks = Array.from(Array(maxBlocks).keys()).filter(b => (b>=base && b <= i)).map(m => `${idPrefix}${m}`)
  let noBlocks = Array.from(Array(maxBlocks).keys()).filter(b => b > i).map(m => `${idPrefix}${m}`)
  baseBlocks.forEach(b => document.getElementById(b).style.opacity=1)
  yesBlocks.forEach(b => document.getElementById(b).style.opacity=0.5)
  noBlocks.forEach(b => document.getElementById(b).style.opacity=blockOpDecay(parseInt(b.split('-')[3]), i))
}
function highlightBlocks(idPrefix, i, base) {
  let yesBlocks = Array.from(Array(maxBlocks).keys()).map(m => `${idPrefix}${m}`)
  let noBlocks = Array.from(Array(maxBlocks).keys()).filter(b => b > i).map(m => `${idPrefix}${m}`)
  yesBlocks.forEach(b => document.getElementById(b).style.opacity=1)
  noBlocks.forEach(b => document.getElementById(b).style.opacity=blockOpDecay(parseInt(b.split('-')[3]), i))
}
function resetGenBlock(config, genClicked) {
  let length = config.recipient % 10
  for(let i = 0; i < maxBlocks; i++ ) {
    let block = document.getElementById(`gen${config.trial}-recipient-block-${i}`)
    block.style.opacity = (i < length)? 1 : blockOpDecay(i, length)
  }
  genBlocksEffects(config, genClicked)
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

  const delta = Math.round(endPos - startPos) + 8;
  (delta > 0) && (agentStone.style.left = `${delta}px`);

  let initLen = config.recipient % 10
  let targetLen = config.result % 10
  let hist = document.getElementById(`task-training-displayhist-${config.trial}`)

  if (targetLen == 1) {
    setTimeout(()=> {
      hist.style.opacity = 0
      hist.style.display = 'flex'
      fadeIn(hist)
    }, 2500)
  } else {
    setTimeout(() => {
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
function shuffleArray(array) {
  for (let i = array.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [array[i], array[j]] = [array[j], array[i]];
  }
  return array
}

function disableFormInputs (formId) {
  const form = document.getElementById(formId);
  const inputs = form.elements;
  (Object.keys(inputs)).forEach((input) => inputs[input].disabled = true);
}
function isFilled (formID) {
  let notFilled = false;
  const nulls = [ '', '--', '', '--', '', '--' ];
  const form = document.getElementById(formID);
  const inputs = form.elements;
  (Object.keys(inputs)).forEach((input, idx) => {
    let field = inputs[input];
    notFilled = (notFilled || (field.value === nulls[idx]));
  });
  return (!notFilled)
}

function findAllIndex(element, array) {
  let indices = [];
  let idx = array.indexOf(element);
  while (idx != -1) {
    indices.push(idx);
    idx = array.indexOf(element, idx + 1);
  }
  return(indices);
}
