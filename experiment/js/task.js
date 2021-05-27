
const mode = 'dev' // '' for production, 'dev' for development, 'flask' for flask-app

/** Pick a condition */
const cond = 'row'
const cond_dict = {
  'row': [1,2,3],
  'col': [1,4,7],
  'ldg': [1,5,9],
  'rdg': [3,5,7],
}
console.log(cond)

/** Prep task data for experiment */
let learnConfigs = config.filter(c => c.phase === 'tab' & cond_dict[cond].indexOf(c.trial) > -1)
learnConfigs.map((lc, idx) => {
  lc['ptrial'] = `${lc['phase']}-${lc['trial']}`
  lc['trial'] = idx+1
  lc['task_phase'] = 'learn'
})
let learnClicked = Array(learnConfigs.length).fill(0);

let genConfigs = config.filter(c => c.phase === 'tab' & cond_dict[cond].indexOf(c.trial) < 0).concat(config.filter(c => c.phase === 'gen'))
genConfigs = shuffleArray(genConfigs)
genConfigs.map((gc, idx) => {
  gc['ptrial'] = `${gc['phase']}-${gc['trial']}`
  gc['trial'] = idx+1
  gc['task_phase'] = 'gen'
})
let genClicked = Array(genConfigs.length).fill(0);

/** Prep task data for save */
let subjectData = {};

let trialData = {
  "phase": [],
  "tid": [],
  "sid": [],
  "agent": [],
  "recipient": [],
  "result": [],
};
learnConfigs.forEach(c => {
  trialData['phase'].push('learn');
  trialData['tid'].push(c.trial);
  trialData['sid'].push(c.ptrial);
  trialData['agent'].push(c.agent);
  trialData['recipient'].push(c.recipient);
  trialData['result'].push(c.result);
})
genConfigs.forEach(c => {
  trialData['phase'].push('gen');
  trialData['tid'].push(c.trial);
  trialData['sid'].push(c.ptrial);
  trialData['agent'].push(c.agent);
  trialData['recipient'].push(c.recipient);
  trialData['result'].push('0');
})

// // Demo pre-train materials
// let ptDivPrefix = 'task-pretrain'
// let box = createCustomElement("div", "box", `${ptDivPrefix}-box`);
// let taskBox = createCustomElement("div", "task-box", `${ptDivPrefix}-taskbox`);

// let taskNum = createText('h2', `Power detection results`);
// taskBox.append(taskNum);

// let displayBox = createCustomElement("div", "pt-display-box", `${ptDivPrefix}-displaybox`);
// displayBox = createPretrainings(displayBox)

// const buttonGroup = createCustomElement("div", "button-group-vc", `p`);
// buttonGroup.append(createBtn(`${ptDivPrefix}-next-btn`, "Next", false));

// taskBox.append(displayBox);
// taskBox.append(buttonGroup);
// box.append(taskBox);
// document.getElementById(ptDivPrefix).append(box);


// Generate learning frame
learnDivPrefix = 'task-training'
coreLearnDiv = document.getElementById(learnDivPrefix)
for(let i = 0; i < learnConfigs.length; i++ ) {
  let { _, trial, agent, recipient, result } = learnConfigs[i];
  let config = { trial: i+1, taskId: trial, agent, recipient, result }

  let trialId = config.trial;
  let display = (mode==='dev'|i===0)? 'flex': 'none';

  let box = createCustomElement("div", "box", `${learnDivPrefix}-box-${trialId}`);
  let taskBox = createCustomElement("div", "task-box", `${learnDivPrefix}-taskbox-${trialId}`);


  let taskNum = createText('h2', `${trialId}/${learnConfigs.length}`);
  taskBox.append(taskNum);

  let displayBox = createCustomElement("div", "display-box", `${learnDivPrefix}-displaybox-${trialId}`);

  let displayMain = createCustomElement("div", "display-main", `${learnDivPrefix}-displaymain-${trialId}`);
  displayMain = createInitStones(config, displayMain);

  let displayHist = createCustomElement("div", "display-hist", `${learnDivPrefix}-displayhist-${trialId}`);
  displayHist = createInitHistory(config, displayHist)
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
  coreLearnDiv.append(box);

  /** Button functionalities */
  const playBtn = document.getElementById(`${learnDivPrefix}-test-btn-${trialId}`);
  const nextBtn = document.getElementById(`${learnDivPrefix}-next-btn-${trialId}`);

  playBtn.onclick = () => {
    playBtn.disabled = true;
    if (learnClicked[i] > 0) {
      clearElement(`${learnDivPrefix}-displaymainspace-${config.trial}`)
      clearElement(`${learnDivPrefix}-displaymainagent-${config.trial}`)
      clearElement(`${learnDivPrefix}-displaymainrecipient-${config.trial}`)
      createInitStones(config, displayMain)
    }
    playEffects(config, learnClicked[i]);
    setTimeout(() => {
      nextBtn.disabled = false;
      playBtn.disabled = false;
      playBtn.innerText = 'Test again'
    }, 2000);
    learnClicked[i] += 1;
  }
  nextBtn.onclick = () => {
    nextBtn.disabled = true;
    const nextDiv = (i === learnConfigs.length-1)? 'task-guess': `task-training-box-${i+2}`;
    // (mode !== 'dev')? hide(`box-${trialId}`): null;
    showNext(nextDiv);
  }

}

// Free response
(mode === 'dev')? document.getElementById('task-guess').style.display = 'flex': null;
let inputForm = document.getElementById('task-guess-input-form')
let okBtn = document.getElementById('task-guess-input-submit-btn')

inputForm.onchange = () => isFilled('task-guess-input-form')? okBtn.disabled = false: null;
okBtn.onclick = () => {
  let inputs = inputForm.elements;
  Object.keys(inputs).forEach(id => subjectData[inputs[id].name] = inputs[id].value);
  okBtn.disabled = true;
  disableFormInputs('task-guess-input-form');
  console.log(subjectData)
  if (mode !== 'dev') {
    // hide("core-learn-form-div");
    showNext("task-gen-box-1")
  }
}


// Generate gen tasks
let genDivPrefix = 'task-gen'
let genDiv = document.getElementById(genDivPrefix)
for(let i = 0; i < genConfigs.length; i++ ) {

  let trialId = genConfigs[i].trial
  let display = (mode==='dev')? 'flex': 'none';

  let box = createCustomElement("div", "box", `${genDivPrefix}-box-${trialId}`);

  let taskBox = createCustomElement("div", "task-box", `${genDivPrefix}-taskbox-${trialId}`);
  let taskNum = createText('h2', `${trialId}/${genConfigs.length}`);
  taskBox.append(taskNum);

  let displayBox = createCustomElement("div", "display-box", `${genDivPrefix}-displaybox-${trialId}`);
  let displayMain = createCustomElement("div", "display-main", `${genDivPrefix}-displaymain-${trialId}`);
  displayMain = createGenStones(genConfigs[i], displayMain);
  displayBox.append(displayMain)

  const buttonGroup = createCustomElement("div", "button-group-vc", `learn${trialId}`);
  buttonGroup.append(createBtn(`${genDivPrefix}-reset-btn-${trialId}`, "Reset", false));
  buttonGroup.append(createBtn(`${genDivPrefix}-confirm-btn-${trialId}`, "Confirm", false));

  taskBox.append(displayBox);
  // taskBox.append(buttonGroup);
  box.append(taskBox);
  box.append(buttonGroup);
  genDiv.append(box);
  box.style.display = display

  /** Effects and button functionalities */
  genBlocksEffects(genConfigs[i], genClicked)
  handleGenSelection(genConfigs[i])
  let resetBtn = document.getElementById(`${genDivPrefix}-reset-btn-${trialId}`)
  let confirmBtn = document.getElementById(`${genDivPrefix}-confirm-btn-${trialId}`)
  resetBtn.onclick = () => {
    genClicked[i] = 0
    confirmBtn.disabled = true;
    resetGenBlock(genConfigs[i], genClicked)
  }
  confirmBtn.onclick = () => {
    disableBlocks(genConfigs[i])
    resetBtn.disabled = true
    confirmBtn.disabled = true;
    trialData.result[learnConfigs.length+i] = '4'+getCurrentSelection(genConfigs[i])
    // const nextDiv = (i === genConfigs.length-1)? '': `task-gen-box-${i+2}`;
    // showNext(nextDiv);
  }
}
