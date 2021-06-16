
/** Ad hoc setups */
const defaultStone = { 'borderWidth': '8px', 'mar': 5, 'len': 60 };
const smallStone = { 'borderWidth': '3px', 'mar': 3, 'len': 20 };
const maxBlocks = 12

/** Basic helper functions */
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

/** Task functions */
function createInitStones(config, parentDiv, learnDivPrefix) {
  let spaceDiv = createCustomElement("div", "display-main-space", `${learnDivPrefix}-displaymainspace-${config.trial}`)
  let agentDiv = createCustomElement("div", "display-main-agent", `${learnDivPrefix}-displaymainagent-${config.trial}`)
  let recipientDiv = createCustomElement("div", "display-main-recipient", `${learnDivPrefix}-displaymainrecipient-${config.trial}`)
  agentDiv.append(createAgentStone(`${learnDivPrefix}-${config.trial}-agent`, config.agent, config.color))
  recipientDiv.append(createBlocks(`${learnDivPrefix}-${config.trial}-recipient`, config))
  parentDiv.append(spaceDiv)
  parentDiv.append(agentDiv)
  parentDiv.append(recipientDiv)
  return(parentDiv);
}
function createInitHistory(config, parentDiv, learnDivPrefix, showText = true) {
  let spaceDiv = createCustomElement("div", "display-main-space", `${learnDivPrefix}-displaymainspace-hist-${config.trial}`)
  let agentDiv = createCustomElement("div", "display-main-agent", `${learnDivPrefix}-displaymainagent-hist-${config.trial}`)
  let recipientDiv = createCustomElement("div", "display-main-recipient", `${learnDivPrefix}-displaymainrecipient-hist-${config.trial}`)

  if (showText) {
    let textDiv = createCustomElement('div', 'hist-text', id=`learn${config.trial}-hist-text`)
    textDiv.append(createText('h2', 'Before'))
    spaceDiv.append(textDiv);
  }
  agentDiv.append(createAgentStone(`${learnDivPrefix}-${config.trial}-hist-agent`, config.agent, config.color))
  recipientDiv.append(createBlocks(`${learnDivPrefix}-${config.trial}-hist-recipient`, config))

  parentDiv.append(spaceDiv)
  parentDiv.append(agentDiv)
  parentDiv.append(recipientDiv)
  return(parentDiv);
}
function createSum(config, divPrefix) {
  let sumBox = createCustomElement('div', 'summary-box', `${divPrefix}-box-${config.trial}`);

  let sumBoforeDiv = createCustomElement("div", "display-hist", `${divPrefix}-beforediv-${config.trial}`);
  sumBoforeDiv = createSumBefore(config, sumBoforeDiv, divPrefix)

  let sumAfterDiv = createCustomElement("div", "display-after", `${divPrefix}-afterdiv-${config.trial}`);
  sumAfterDiv = createSumAfter(config, sumAfterDiv, divPrefix)

  sumBox.append(sumBoforeDiv)
  sumBox.append(sumAfterDiv)
  return sumBox
}
function createSumBefore(config, parentDiv, divPrefix) {
  let agentDiv = createCustomElement("div", "display-main-agent", `${divPrefix}-displaymainagent-after-${config.trial}`)
  let recipientDiv = createCustomElement("div", "display-main-recipient", `${divPrefix}-displaymainrecipient-after-${config.trial}`)

  agentDiv.append(createAgentStone(`${divPrefix}-${config.trial}-after-agent`, config.agent, config.color))
  recipientDiv.append(createBlocks(`${divPrefix}-${config.trial}-after-recipient`, config))

  parentDiv.append(agentDiv)
  parentDiv.append(recipientDiv)
  return(parentDiv);

}
function createSumAfter(config, parentDiv, divPrefix) {
  let agentDiv = createCustomElement("div", "display-main-agent-after", `${divPrefix}-displaymainagent-after-${config.trial}`)
  let recipientDiv = createCustomElement("div", "display-main-recipient", `${divPrefix}-displaymainrecipient-after-${config.trial}`)

  agentDiv.append(createAgentStone(`${divPrefix}-${config.trial}-after-agent`, config.agent, config.color))
  recipientDiv.append(createBlocks(`${divPrefix}-${config.trial}-after-recipient`, config, false))

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
function createAgentStone(id, nStripes = 1, color='red', base = 40, r = 25) {
  nStripes = Math.floor(nStripes/10)
  const getDelta = (x) => (-x + Math.sqrt(2*(r**2)-x**2))/2

  let agentDiv = createCustomElement("div", "agent-stone-div", `${id}-div`);
  let agentStoneSvg = createCustomElement('svg', 'stone-svg', id)
  let circleSvg = '<circle class="agent-stone" cx="40" cy="40" r="30" />'
  let stripes = ''

  switch (nStripes) {
    case 1:
      stripes = `<line class="agent-stone-stripe" x1="${base+getDelta(0)}" y1="${base-getDelta(0)}" x2="${base-getDelta(0)}" y2="${base+getDelta(0)}" stroke="${color}" />`;
      break;
    case 2:
      stripes = `<line class="agent-stone-stripe" x1="${base+getDelta(15)}" y1="${base-getDelta(15)-15}" x2="${base-getDelta(15)-15}" y2="${base+getDelta(15)}" stroke="${color}" />` + '\n' +
      `<line class="agent-stone-stripe" x1="${base+getDelta(15)+15}" y1="${base-getDelta(15)}" x2="${base-getDelta(15)}" y2="${base+getDelta(15)+15}" stroke="${color}" />`
      break;
    case 3:
      stripes = `<line class="agent-stone-stripe" x1="${base+getDelta(0)}" y1="${base-getDelta(0)}" x2="${base-getDelta(0)}" y2="${base+getDelta(0)}" stroke="${color}" />` + '\n' +
      `<line class="agent-stone-stripe" x1="${base+getDelta(20)}" y1="${base-getDelta(20)-20}" x2="${base-getDelta(20)-20}" y2="${base+getDelta(20)}" stroke="${color}" />` + '\n' +
      `<line class="agent-stone-stripe" x1="${base+getDelta(20)+20}" y1="${base-getDelta(20)}" x2="${base-getDelta(20)}" y2="${base+getDelta(20)+20}" stroke="${color}" />`
      break;
    case 4:
      stripes = `<line class="agent-stone-stripe" x1="${base+getDelta(8)}" y1="${base-getDelta(8)-8}" x2="${base-getDelta(8)-8}" y2="${base+getDelta(8)}" stroke="${color}" />` + '\n' +
      `<line class="agent-stone-stripe" x1="${base+getDelta(8)+8}" y1="${base-getDelta(8)}" x2="${base-getDelta(8)}" y2="${base+getDelta(8)+8}" stroke="${color}" />` + '\n' +
      `<line class="agent-stone-stripe" x1="${base+getDelta(25)}" y1="${base-getDelta(25)-25}" x2="${base-getDelta(25)-25}" y2="${base+getDelta(25)}" stroke="${color}" />` + '\n' +
      `<line class="agent-stone-stripe" x1="${base+getDelta(25)+25}" y1="${base-getDelta(25)}" x2="${base-getDelta(25)}" y2="${base+getDelta(25)+25}" stroke="${color}" />`
      break;
  }
  agentStoneSvg.innerHTML = circleSvg + stripes
  agentDiv.append(agentStoneSvg)
  return agentDiv
}
function createBlocks(id, stoneOpts, isInit = true) {
  let div = createCustomElement("div", "recipient-stone-div", `${id}-blocks-all`);
  let length = isInit? stoneOpts.recipient % 10 : stoneOpts.result % 10
  let max =  (stoneOpts.phase=='gen')? maxBlocks: stoneOpts.result % 10
  for(let i = 0; i < max; i++ ) {
    let block = createCustomElement("div", "recipient-block", `${id}-block-${i}`)
    block.style.opacity = (i < length)? 1 : (stoneOpts.phase=='gen')? blockOpDecay(i, length) : 0
    div.append(block)
  }
  return(div);
}
function createGenStones(config, parentDiv, genDivPrefix) {
  let spaceDiv = createCustomElement("div", "display-main-space", `${genDivPrefix}-${config.trial}-display-space-div`)
  let agentDiv = createCustomElement("div", "display-main-agent", `${genDivPrefix}-${config.trial}-display-agent-div`)
  let recipientDiv = createCustomElement("div", "display-main-recipient", `${genDivPrefix}-${config.trial}-display-recipient-div`)

  agentDiv.append(createAgentStone(`${genDivPrefix}-${config.trial}-agent`, config.agent, config.color));
  recipientDiv.append(createBlocks(`${genDivPrefix}-${config.trial}-recipient`, config));

  parentDiv.append(spaceDiv)
  parentDiv.append(agentDiv)
  parentDiv.append(recipientDiv)
  return(parentDiv);
}
function blockOpDecay(index, base) {
  if ((index === base) && (index < maxBlocks)) {
    return 0.15
  } else {
    if ((index === base+1) && (index < maxBlocks)) {
      return 0.05
    } else {
      return 0
    }
  }
  // return (index > base + 1)? 0: 0.1 - 0.001*(index - base)
}
function genBlocksEffects(config, genDivPrefix, genClicked) {
  for(let i = 0; i < maxBlocks; i++ ) {
    let idPrefix = `${genDivPrefix}-${config.trial}-recipient-block-`
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
function handleGenSelection(config,genDivPrefix) {
  let blocksDiv = document.getElementById(`${genDivPrefix}-${config.trial}-recipient-blocks-all`)
  let resetBtn = document.getElementById(`${genDivPrefix}-reset-btn-${config.trial}`)
  let confirmBtn = document.getElementById(`${genDivPrefix}-confirm-btn-${config.trial}`)
  blocksDiv.onclick = () => {
    resetBtn.disabled = false
    confirmBtn.disabled = false
  }
}
function getCurrentSelection(config, genDivPrefix) {
  let blockOps = []
  for(let i = 0; i < maxBlocks; i++ ) {
    blockOps.push(document.getElementById(`${genDivPrefix}-${config.trial}-recipient-block-${i}`).style.opacity)
  }
  return(findAllIndex('1',blockOps).length)
}
function disableBlocks(config, genDivPrefix) {
  document.getElementById(`${genDivPrefix}-${config.trial}-recipient-blocks-all`).onclick = null
  for(let i = 0; i < maxBlocks; i++ ) {
    let blockDiv = document.getElementById(`${genDivPrefix}-${config.trial}-recipient-block-${i}`)
    blockDiv.onmousemove = () => null
    blockDiv.onmouseout = () => null
    blockDiv.onclick = () => null
  }
}
function highlightBlocksOnMouseOver(idPrefix, i, base) {
  let baseBlocks = Array.from(Array(base).keys()).map(m => `${idPrefix}${m}`)
  let yesBlocks = Array.from(Array(maxBlocks).keys()).filter(b => (b>=base && b <= i)).map(m => `${idPrefix}${m}`)
  let noBlocks = Array.from(Array(maxBlocks).keys()).filter(b => b > i+2).map(m => `${idPrefix}${m}`)
  baseBlocks.forEach(b => document.getElementById(b).style.opacity=1)
  yesBlocks.forEach(b => document.getElementById(b).style.opacity=0.5)
  noBlocks.forEach(b => document.getElementById(b).style.opacity=0)
  if (i+1 < maxBlocks) {
    document.getElementById(`${idPrefix}${i+1}`).style.opacity = 0.15
  }
  if (i+2 < maxBlocks) {
    document.getElementById(`${idPrefix}${i+2}`).style.opacity = 0.05
  }
}
function highlightBlocks(idPrefix, i, base) {
  let yesBlocks = Array.from(Array(maxBlocks).keys()).map(m => `${idPrefix}${m}`)
  let noBlocks = Array.from(Array(maxBlocks).keys()).filter(b => b > i).map(m => `${idPrefix}${m}`)
  yesBlocks.forEach(b => document.getElementById(b).style.opacity=1)
  noBlocks.forEach(b => document.getElementById(b).style.opacity=0) //blockOpDecay(parseInt(b.split('-')[3]), i))
  if (i+1 < maxBlocks) {
    document.getElementById(`${idPrefix}${i+1}`).style.opacity = 0.15
  }
  if (i+2 < maxBlocks) {
    document.getElementById(`${idPrefix}${i+2}`).style.opacity = 0.05
  }
}
function resetGenBlock(config, genDivPrefix, genClicked) {
  let length = config.recipient % 10
  for(let i = 0; i < maxBlocks; i++ ) {
    let block = document.getElementById(`${genDivPrefix}-${config.trial}-recipient-block-${i}`)
    block.style.opacity = (i < length)? 1 : blockOpDecay(i, length)
  }
  genBlocksEffects(config, genDivPrefix, genClicked)
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
function clearInitStones(learnDivPrefix, config) {
  clearElement(`${learnDivPrefix}-displaymainspace-${config.trial}`)
  clearElement(`${learnDivPrefix}-displaymainagent-${config.trial}`)
  clearElement(`${learnDivPrefix}-displaymainrecipient-${config.trial}`)
}
function getCurrentLocation (id) {
  let rect = {top: 0, bottom: 0, left: 0, right: 0};
  const pos = document.getElementById(id).getBoundingClientRect();
  rect.top = pos.top;
  rect.bottom = pos.bottom;
  rect.left = pos.left;
  rect.right = pos.right;
  return rect;
}

function playEffects (config, learnDivPrefix, clicked=0) {

  if (!(document.body.contains(document.getElementById(`${learnDivPrefix}-${config.trial}-agent-div`)))) {
    console.log('???')
  }

  const agentStone = document.getElementById(`${learnDivPrefix}-${config.trial}-agent-div`);
  const startPos = getCurrentLocation(`${learnDivPrefix}-${config.trial}-agent`).right;
  const endPos = getCurrentLocation(`${learnDivPrefix}-${config.trial}-recipient-blocks-all`).left;

  const delta = Math.round(endPos - startPos) + 8;
  (delta > 0) && (agentStone.style.left = `${delta}px`);

  let initLen = config.recipient % 10
  let targetLen = parseInt(config.result) % 10
  let agentStripe = Math.floor(parseInt(config.agent) % Math.pow(10,2) / Math.pow(10,1))
  let hist = document.getElementById(`${learnDivPrefix}-displayhist-${config.trial}`)

  if (agentStripe == 1) {
    setTimeout(()=> {
      hist.style.opacity = 0
      hist.style.display = 'flex'
      fadeIn(hist)
    }, 2500)
  } else {
    setTimeout(() => {
      for (let i = initLen; i < targetLen; i++ ) {
        fadeIn(document.getElementById(`${learnDivPrefix}-${config.trial}-recipient-block-${i}`))
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
// function createPretrainings(parentDiv) {
//   for(let i = 0; i < 3; i++ ) {
//     let obsId = i + 1
//     let div = createCustomElement('div', 'detect-div', `pretrain-detect-div-${obsId}`)
//     let agent = createCustomElement('div', 'detect-div-agent', `pretrain-detect-div-agent-${obsId}`)
//     agent.append(createAgentStone(`pretrain-detect-agent-${obsId}`, (i+3)*10+1))
//     let power = createCustomElement('div', 'detect-div-power', `pretrain-detect-div-power-${obsId}`)
//     power.innerHTML = `<p>${'&#9733;'.repeat(i+1)}</p>`
//     div.append(agent)
//     div.append(power)
//     parentDiv.append(div)
//   }
//   return parentDiv
// }
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

/** Data functions */
function fmtConfig(dataArr, batch, phase, agentColor = 'red') {
  let fmtted = []
  dataArr.forEach((data, idx) => {
    dd = {}
    dd['id'] =`t${data['trial']}`
    dd['trial'] = idx+1
    dd['batch'] = batch
    dd['phase'] = phase
    dd['agent'] = data['agent']
    dd['recipient'] = data['recipient']
    dd['result'] = (phase==='gen')? '': data['result']
    dd['color'] = agentColor
    fmtted.push(dd)
  })
  return fmtted
}
function prepTrialData (configsArr) {
  let trialData = {
    "batch": [],
    "phase": [],
    "trial": [],
    "id": [],
    "agent": [],
    "agent-color": [],
    "recipient": [],
    "result": [],
  }
  configsArr.forEach(conf => {
    trialData['batch'].push(conf['batch']);
    trialData['phase'].push(conf['phase']);
    trialData['trial'].push(conf['trial']);
    trialData['id'].push(conf['id']);
    trialData['agent'].push(conf['agent']);
    trialData['agent-color'].push(conf['color']);
    trialData['recipient'].push(conf['recipient']);
    trialData['result'].push(conf['result']);
  })
  return trialData
}

/** Page functions */
function createLearnTask(learnDivPrefix, learnConfig, total=0) {
  let trialId = learnConfig.trial;
  let display = (mode==='dev'|trialId===1)? 'flex': 'none';

  let box = createCustomElement("div", "box", `${learnDivPrefix}-box-${trialId}`);
  let taskBox = createCustomElement("div", "task-box", `${learnDivPrefix}-taskbox-${trialId}`);

  if (total > 1) {
    let taskNum = createText('h2', `${trialId}/${total}`);
    taskBox.append(taskNum);
  }

  let displayBox = createCustomElement("div", "display-box", `${learnDivPrefix}-displaybox-${trialId}`);
  let displayMain = createCustomElement("div", "display-main", `${learnDivPrefix}-displaymain-${trialId}`);
  displayMain = createInitStones(learnConfig, displayMain, learnDivPrefix);

  let displayHist = createCustomElement("div", "display-hist", `${learnDivPrefix}-displayhist-${trialId}`);
  displayHist = createInitHistory(learnConfig, displayHist, learnDivPrefix)
  displayHist.style.opacity = 0
  displayBox.append(displayHist)
  displayBox.append(displayMain)

  const buttonGroup = createCustomElement("div", "button-group-vc", `learn${trialId}`);
  buttonGroup.append(createBtn(`${learnDivPrefix}-test-btn-${trialId}`, "Test", true));
  buttonGroup.append(createBtn(`${learnDivPrefix}-next-btn-${trialId}`, "Next", false));
  taskBox.append(displayBox);

  // taskBox.append(buttonGroup);
  box.append(taskBox);
  box.append(buttonGroup)
  box.style.display = display;

  return box
}
function createInputForm(formPrefix) {
  let box = createCustomElement("div", "box", `${formPrefix}-box`);
  box.innerHTML = `
          <div class="display-box" id="${formPrefix}-display-box">
            <form class="input-form" id="${formPrefix}-input-form">
              <p>
                <b>What is your best guess about how these mysterious stones work?</b>
                (Please refer to stones as <i>active</i> and <i>inactive</i>,
                and be specific about <i>what properties you think matter or do not matter for the effects,
                and how they do so</i>.)
                <br />
              </p>
              <textarea name="${formPrefix}_input" id="${formPrefix}_input" placeholder="Type here"></textarea>
              <p class="incentive">Remember there is a $0.50 bonus if you guess correctly, and nonsense answers will result in a zero bonus or hit rejection.</p>
              <p>How certain are you?
                <select name="${formPrefix}_certainty" id="${formPrefix}_certainty" class="input-rule">
                  <option value="--" SELECTED>
                    <option value="10">10 - Very certain</option>
                    <option value="9">9</option>
                    <option value="8">8</option>
                    <option value="7">7</option>
                    <option value="6">6</option>
                    <option value="5">5 - Moderately</option>
                    <option value="4">4</option>
                    <option value="3">3</option>
                    <option value="2">2</option>
                    <option value="1">1</option>
                    <option value="0">0 - Not sure at all</option>
                </select>
              </p>
            </form>
          </div>
          <div class="button-group-vc" id="${formPrefix}-button-group-vc">
            <button id="${formPrefix}-input-submit-btn" disabled=true>OK</button>
          </div>`
  return box
}
function createGenTask(genDivPrefix, genConfigs, total = 0) {
  let trialId = genConfigs.trial
  let display = (mode==='dev')? 'flex': 'none';

  let box = createCustomElement("div", "box", `${genDivPrefix}-box-${trialId}`);
  let taskBox = createCustomElement("div", "task-box", `${genDivPrefix}-taskbox-${trialId}`);

  if (total > 1) {
    let taskNum = createText('h2', `${trialId}/${total}`);
    taskBox.append(taskNum);
  }

  let displayBox = createCustomElement("div", "display-box", `${genDivPrefix}-displaybox-${trialId}`);
  let displayMain = createCustomElement("div", "display-main", `${genDivPrefix}-displaymain-${trialId}`);
  displayMain = createGenStones(genConfigs, displayMain, genDivPrefix);
  displayBox.append(displayMain)

  const buttonGroup = createCustomElement("div", "button-group-vc", `learn${trialId}`);
  buttonGroup.append(createBtn(`${genDivPrefix}-reset-btn-${trialId}`, "Reset", false));
  buttonGroup.append(createBtn(`${genDivPrefix}-confirm-btn-${trialId}`, "Confirm", false));

  taskBox.append(displayBox);
  // taskBox.append(buttonGroup);
  box.append(taskBox);
  box.append(buttonGroup);
  box.style.display = display

  return box
}
