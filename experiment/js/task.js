
const mode = 'dev' // '' for production, 'dev' for development, 'flask' for flask-app

/** Pick a condition */
const cond = 'hard'
console.log(cond)

/** Prep data */
const exp_conds = {
  'easy': {
    'alice': {
      'learn': [1,2,3],
      'gen': [4],
    },
    'bob': {
      'learn': [1,5,8],
      'gen': [11],
    }
  },
  'hard': {
    'alice': {
      'learn': [1,2,3],
      'gen': [4],
    },
    'bob': {
      'learn': [4,6,11],
      'gen': [10],
    }
  }
}

let aliceLearn = fmtConfig(config.filter(c => exp_conds[cond]['alice']['learn'].indexOf(c.trial) > -1), 'alice', 'learn')
let aliceGen = fmtConfig(config.filter(c => exp_conds[cond]['alice']['gen'].indexOf(c.trial) > -1), 'alice', 'gen')

let bobLearn = fmtConfig(config.filter(c => exp_conds[cond]['bob']['learn'].indexOf(c.trial) > -1), 'bob', 'learn')
let bobGen = fmtConfig(config.filter(c => exp_conds[cond]['bob']['gen'].indexOf(c.trial) > -1), 'bob', 'gen')

let usedIndices = [ exp_conds[cond]['alice']['learn'], exp_conds[cond]['alice']['gen'], exp_conds[cond]['bob']['learn'], exp_conds[cond]['bob']['gen']].flat()
let genConfigs =  config.filter(c => usedIndices.indexOf(c.trial) < 0)
genConfigs = fmtConfig(shuffleArray(genConfigs), 'gen', 'gen')

// For page animation
let aliceClicked = Array(aliceLearn.length).fill(0);
let bobClicked = Array(bobLearn.length).fill(0);
let genClicked = Array(genConfigs.length).fill(0);

// Data to save
let subjectData = prepSubjectData([aliceLearn, aliceGen, bobLearn, bobGen, genConfigs].flat())


/** Generate learning frames */
function createLearnTask(learnDivPrefix, learnConfig) {
  let trialId = learnConfig.trial;
  let display = (mode==='dev'|trialId===1)? 'flex': 'none';

  let box = createCustomElement("div", "box", `${learnDivPrefix}-box-${trialId}`);
  let taskBox = createCustomElement("div", "task-box", `${learnDivPrefix}-taskbox-${trialId}`);
  let taskNum = createText('h2', trialId);
  taskBox.append(taskNum);

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


let coreLearnDiv = document.getElementById('task-train-a')
for(let i = 0; i < aliceLearn.length; i++ ) {
  coreLearnDiv.append(createLearnTask('task-train-a', aliceLearn[i]))
}


// coreLearnDiv = document.getElementById(learnDivPrefix)
// for(let i = 0; i < learnConfigs.length; i++ ) {
//   let { _, trial, agent, recipient, result } = learnConfigs[i];
//   let config = { trial: i+1, taskId: trial, agent, recipient, result }

//   let trialId = config.trial;
//   let display = (mode==='dev'|i===0)? 'flex': 'none';

//   let box = createCustomElement("div", "box", `${learnDivPrefix}-box-${trialId}`);
//   let taskBox = createCustomElement("div", "task-box", `${learnDivPrefix}-taskbox-${trialId}`);

//   let taskNum = createText('h2', `${trialId}/${learnConfigs.length}`);
//   taskBox.append(taskNum);

//   let displayBox = createCustomElement("div", "display-box", `${learnDivPrefix}-displaybox-${trialId}`);

//   let displayMain = createCustomElement("div", "display-main", `${learnDivPrefix}-displaymain-${trialId}`);
//   displayMain = createInitStones(config, displayMain);

//   let displayHist = createCustomElement("div", "display-hist", `${learnDivPrefix}-displayhist-${trialId}`);
//   displayHist = createInitHistory(config, displayHist)
//   displayHist.style.opacity = 0

//   displayBox.append(displayHist)
//   displayBox.append(displayMain)

//   const buttonGroup = createCustomElement("div", "button-group-vc", `learn${trialId}`);
//   buttonGroup.append(createBtn(`${learnDivPrefix}-test-btn-${trialId}`, "Test", true));
//   buttonGroup.append(createBtn(`${learnDivPrefix}-next-btn-${trialId}`, "Next", false));

//   taskBox.append(displayBox);
//   // taskBox.append(buttonGroup);
//   box.append(taskBox);
//   box.append(buttonGroup)
//   box.style.display = display;
//   coreLearnDiv.append(box);

//   /** Button functionalities */
//   const playBtn = document.getElementById(`${learnDivPrefix}-test-btn-${trialId}`);
//   const nextBtn = document.getElementById(`${learnDivPrefix}-next-btn-${trialId}`);

//   playBtn.onclick = () => {
//     playBtn.disabled = true;
//     if (learnClicked[i] > 0) {
//       clearElement(`${learnDivPrefix}-displaymainspace-${config.trial}`)
//       clearElement(`${learnDivPrefix}-displaymainagent-${config.trial}`)
//       clearElement(`${learnDivPrefix}-displaymainrecipient-${config.trial}`)
//       createInitStones(config, displayMain)
//     }
//     playEffects(config, learnClicked[i]);
//     setTimeout(() => {
//       nextBtn.disabled = false;
//       playBtn.disabled = false;
//       playBtn.innerText = 'Test again'
//     }, 2000);
//     learnClicked[i] += 1;
//   }
//   nextBtn.onclick = () => {
//     nextBtn.disabled = true;
//     const nextDiv = (i === learnConfigs.length-1)? 'task-guess': `task-training-box-${i+2}`;
//     // (mode !== 'dev')? hide(`box-${trialId}`): null;
//     showNext(nextDiv);
//   }

// }

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


// // Generate gen tasks
// let genDivPrefix = 'task-gen'
// let genDiv = document.getElementById(genDivPrefix)
// for(let i = 0; i < genConfigs.length; i++ ) {

//   let trialId = genConfigs[i].trial
//   let display = (mode==='dev')? 'flex': 'none';

//   let box = createCustomElement("div", "box", `${genDivPrefix}-box-${trialId}`);

//   let taskBox = createCustomElement("div", "task-box", `${genDivPrefix}-taskbox-${trialId}`);
//   let taskNum = createText('h2', `${trialId}/${genConfigs.length}`);
//   taskBox.append(taskNum);

//   let displayBox = createCustomElement("div", "display-box", `${genDivPrefix}-displaybox-${trialId}`);
//   let displayMain = createCustomElement("div", "display-main", `${genDivPrefix}-displaymain-${trialId}`);
//   displayMain = createGenStones(genConfigs[i], displayMain);
//   displayBox.append(displayMain)

//   const buttonGroup = createCustomElement("div", "button-group-vc", `learn${trialId}`);
//   buttonGroup.append(createBtn(`${genDivPrefix}-reset-btn-${trialId}`, "Reset", false));
//   buttonGroup.append(createBtn(`${genDivPrefix}-confirm-btn-${trialId}`, "Confirm", false));

//   taskBox.append(displayBox);
//   // taskBox.append(buttonGroup);
//   box.append(taskBox);
//   box.append(buttonGroup);
//   genDiv.append(box);
//   box.style.display = display

//   /** Effects and button functionalities */
//   genBlocksEffects(genConfigs[i], genClicked)
//   handleGenSelection(genConfigs[i])
//   let resetBtn = document.getElementById(`${genDivPrefix}-reset-btn-${trialId}`)
//   let confirmBtn = document.getElementById(`${genDivPrefix}-confirm-btn-${trialId}`)
//   resetBtn.onclick = () => {
//     genClicked[i] = 0
//     confirmBtn.disabled = true;
//     resetGenBlock(genConfigs[i], genClicked)
//   }
//   confirmBtn.onclick = () => {
//     disableBlocks(genConfigs[i])
//     resetBtn.disabled = true
//     confirmBtn.disabled = true;
//     trialData.result[learnConfigs.length+i] = '4'+getCurrentSelection(genConfigs[i])
//     if (mode!=='dev') {
//       const nextDiv = (i === genConfigs.length-1)? '': `task-gen-box-${i+2}`;
//       showNext(nextDiv);
//     }
//   }
// }
