
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

let aliceLearn = fmtConfig(config.filter(c => exp_conds[cond]['alice']['learn'].indexOf(c.trial) > -1), 'alice', 'learn', 'red')
let aliceGen = fmtConfig(config.filter(c => exp_conds[cond]['alice']['gen'].indexOf(c.trial) > -1), 'alice', 'gen', 'red')

let bobLearn = fmtConfig(config.filter(c => exp_conds[cond]['bob']['learn'].indexOf(c.trial) > -1), 'bob', 'learn', 'green')
let bobGen = fmtConfig(config.filter(c => exp_conds[cond]['bob']['gen'].indexOf(c.trial) > -1), 'bob', 'gen', 'green')

let usedIndices = [ exp_conds[cond]['alice']['learn'], exp_conds[cond]['alice']['gen'], exp_conds[cond]['bob']['learn'], exp_conds[cond]['bob']['gen']].flat()
let genConfigs =  config.filter(c => usedIndices.indexOf(c.trial) < 0)
genConfigs = fmtConfig(shuffleArray(genConfigs), 'gen', 'gen', 'orange')

// For page animation
let aliceLearnClicked = Array(aliceLearn.length).fill(0);
let aliceGenClicked = Array(aliceGen.length).fill(0);
let bobLearnClicked = Array(bobLearn.length).fill(0);
let bobGenClicked = Array(bobGen.length).fill(0);
let genClicked = Array(genConfigs.length).fill(0);

// Data to save
let subjectData = {}
let trialData = prepTrialData([aliceLearn, aliceGen, bobLearn, bobGen, genConfigs].flat())

// Key frame names
const taskCoverA = 'task-cover-a'
const taskTrainA = 'task-train-a'
const taskInputA = 'task-input-a'
const taskGenA = 'task-gen-a'

const taskCoverB = 'task-cover-b'
const taskTrainB = 'task-train-b'
const taskInputB = 'task-input-b'
const taskGenB = 'task-gen-b'

const taskCoverC = 'task-cover-c'
const taskTrainC = 'task-train-c'
const taskInputC = 'task-input-c'
const taskGenC = 'task-gen-c'

/** Alice */
// learning
for(let i = 0; i < aliceLearn.length; i++ ) {
  let config = aliceLearn[i]
  document.getElementById(taskTrainA).append(createLearnTask(taskTrainA, config, aliceLearn.length))
  let trialId = config.trial

  // Button functionalities
  let playBtn = document.getElementById(`${taskTrainA}-test-btn-${trialId}`);
  let nextBtn = document.getElementById(`${taskTrainA}-next-btn-${trialId}`);
  playBtn.onclick = () => {
    let displayMain = document.getElementById(`${taskTrainA}-displaymain-${trialId}`)
    playBtn.disabled = true;
    if (aliceLearnClicked[i] > 0) {
      clearInitStones(taskTrainA, config)
      createInitStones(config, displayMain, taskTrainA)
    }
    playEffects(config, taskTrainA, aliceLearnClicked[i]);
    setTimeout(() => {
      nextBtn.disabled = false;
      playBtn.disabled = false;
      playBtn.innerText = 'Test again'
    }, 2000);
    aliceLearnClicked[i] += 1;
  }
   nextBtn.onclick = () => {
     nextBtn.disabled = true;
     let nextDiv = (i === aliceLearn.length-1)? taskInputA: `${taskTrainA}-box-${i+2}`;
     (mode !== 'dev')? hide(`box-${trialId}`): null;
     showNext(nextDiv);
   }
}

// Free response
(mode === 'dev')? document.getElementById(taskInputA).style.display = 'flex': null;
document.getElementById(taskInputA).append(createInputForm(taskInputA))

let aliceInputForm = document.getElementById(`${taskInputA}-input-form`)
let aliceOkBtn = document.getElementById(`${taskInputA}-input-submit-btn`)
aliceInputForm.onchange = () => isFilled(`${taskInputA}-input-form`)? aliceOkBtn.disabled = false: null;
aliceOkBtn.onclick = () => {
  let inputs = aliceInputForm.elements;
  Object.keys(inputs).forEach(id => subjectData[inputs[id].name] = inputs[id].value);
  aliceOkBtn.disabled = true;
  disableFormInputs(`${taskInputA}-input-form`);
  console.log(subjectData)
  if (mode !== 'dev') {
    // hide("core-learn-form-div");
    showNext("task-gen-box-1")
  }
}

// Generate gen tasks
for(let i = 0; i < aliceGen.length; i++ ) {
  let config = aliceGen[i]
  // console.log(config)
  document.getElementById(taskGenA).append(createGenTask(taskGenA, config, aliceGen.length))

  /** Effects and button functionalities */
  genBlocksEffects(config, taskGenA, aliceGenClicked)
  handleGenSelection(config, taskGenA)
  let resetBtn = document.getElementById(`${taskGenA}-reset-btn-${config.trial}`)
  let confirmBtn = document.getElementById(`${taskGenA}-confirm-btn-${config.trial}`)
  resetBtn.onclick = () => {
    aliceGen[i] = 0
    confirmBtn.disabled = true;
    resetGenBlock(config, taskGenA, aliceGen)
  }
  confirmBtn.onclick = () => {
    disableBlocks(config, taskGenA)
    resetBtn.disabled = true
    confirmBtn.disabled = true;
    trialData.result[aliceLearn.length+i] = '0'+getCurrentSelection(config, taskGenA)
    console.log(trialData)
    if (mode!=='dev') {
      const nextDiv = (i === aliceGen.length-1)? '': `${taskGenA}-box-${i+2}`;
      showNext(nextDiv);
    }
  }
}


/** Bob */
// learning
for(let i = 0; i < bobLearn.length; i++ ) {
  let config = bobLearn[i]
  document.getElementById(taskTrainB).append(createLearnTask(taskTrainB, config, bobLearn.length))
  let trialId = config.trial

  // Button functionalities
  let playBtn = document.getElementById(`${taskTrainB}-test-btn-${trialId}`);
  let nextBtn = document.getElementById(`${taskTrainB}-next-btn-${trialId}`);
  playBtn.onclick = () => {
    let displayMain = document.getElementById(`${taskTrainB}-displaymain-${trialId}`)
    playBtn.disabled = true;
    if (bobLearnClicked[i] > 0) {
      clearInitStones(taskTrainB, config)
      createInitStones(config, displayMain, taskTrainB)
    }
    playEffects(config, taskTrainB, bobLearnClicked[i]);
    setTimeout(() => {
      nextBtn.disabled = false;
      playBtn.disabled = false;
      playBtn.innerText = 'Test again'
    }, 2000);
    bobLearnClicked[i] += 1;
  }
   nextBtn.onclick = () => {
     nextBtn.disabled = true;
     let nextDiv = (i === bobLearn.length-1)? taskInputB: `${taskTrainB}-box-${i+2}`;
     (mode !== 'dev')? hide(`box-${trialId}`): null;
     showNext(nextDiv);
   }
}

// Free response
(mode === 'dev')? document.getElementById(taskInputB).style.display = 'flex': null;
document.getElementById(taskInputB).append(createInputForm(taskInputB))

let bobInputForm = document.getElementById(`${taskInputB}-input-form`)
let bobOkBtn = document.getElementById(`${taskInputB}-input-submit-btn`)
bobInputForm.onchange = () => isFilled(`${taskInputB}-input-form`)? bobOkBtn.disabled = false: null;
bobOkBtn.onclick = () => {
  let inputs = bobInputForm.elements;
  Object.keys(inputs).forEach(id => subjectData[inputs[id].name] = inputs[id].value);
  bobOkBtn.disabled = true;
  disableFormInputs(`${taskInputB}-input-form`);
  console.log(subjectData)
  if (mode !== 'dev') {
    // hide("core-learn-form-div");
    showNext("task-gen-box-1")
  }
}

// Generate gen tasks
for(let i = 0; i < bobGen.length; i++ ) {
  let config = bobGen[i]
  // console.log(config)
  document.getElementById(taskGenB).append(createGenTask(taskGenB, config, bobGen.length))

  /** Effects and button functionalities */
  genBlocksEffects(config, taskGenB, bobGenClicked)
  handleGenSelection(config, taskGenB)
  let resetBtn = document.getElementById(`${taskGenB}-reset-btn-${config.trial}`)
  let confirmBtn = document.getElementById(`${taskGenB}-confirm-btn-${config.trial}`)
  resetBtn.onclick = () => {
    bobGen[i] = 0
    confirmBtn.disabled = true;
    resetGenBlock(config, taskGenB, bobGen)
  }
  confirmBtn.onclick = () => {
    disableBlocks(config, taskGenB)
    resetBtn.disabled = true
    confirmBtn.disabled = true;
    let prevs = [ aliceLearn.length, aliceGen,length, bobLearn.length ].reduce((a, b) => a + b, 0)
    trialData.result[prevs+i] = '0'+getCurrentSelection(config, taskGenC)
    console.log(trialData)
    if (mode!=='dev') {
      const nextDiv = (i === bobGen.length-1)? '': `${taskGenB}-box-${i+2}`;
      showNext(nextDiv);
    }
  }
}


/** Composition */
let compDiv = document.getElementById(taskTrainC);
let aliceSummaryDiv = createCustomElement('div', 'summary-div', 'alice-summary-div');
let bobSummaryDiv = createCustomElement('div', 'summary-div', 'bob-summary-div');

for(let i = 0; i < aliceLearn.length; i++ ) {
  aliceSummaryDiv.append(createSum(aliceLearn[i], 'alice-sum'))
}

for(let i = 0; i < bobLearn.length; i++ ) {
  bobSummaryDiv.append(createSum(bobLearn[i], 'bob-sum'))
}

compDiv.append(aliceSummaryDiv);
compDiv.append(bobSummaryDiv);

// Free response
(mode === 'dev')? document.getElementById(taskInputC).style.display = 'flex': null;
document.getElementById(taskInputC).append(createInputForm(taskInputC))

let compInputForm = document.getElementById(`${taskInputC}-input-form`)
let compOkBtn = document.getElementById(`${taskInputC}-input-submit-btn`)
compInputForm.onchange = () => isFilled(`${taskInputC}-input-form`)? compOkBtn.disabled = false: null;
compOkBtn.onclick = () => {
  let inputs = compInputForm.elements;
  Object.keys(inputs).forEach(id => subjectData[inputs[id].name] = inputs[id].value);
  compOkBtn.disabled = true;
  disableFormInputs(`${taskInputC}-input-form`);
  console.log(subjectData)
  if (mode !== 'dev') {
    // hide("core-learn-form-div");
    showNext("task-gen-box-1")
  }
}

// Generate gen tasks
for(let i = 0; i < genConfigs.length; i++ ) {
  let config = genConfigs[i]
  // console.log(config)
  document.getElementById(taskGenC).append(createGenTask(taskGenC, config, genConfigs.length))

  /** Effects and button functionalities */
  genBlocksEffects(config, taskGenC, genClicked)
  handleGenSelection(config, taskGenC)
  let resetBtn = document.getElementById(`${taskGenC}-reset-btn-${config.trial}`)
  let confirmBtn = document.getElementById(`${taskGenC}-confirm-btn-${config.trial}`)
  resetBtn.onclick = () => {
    bobGen[i] = 0
    confirmBtn.disabled = true;
    resetGenBlock(config, taskGenC, bobGen)
  }
  confirmBtn.onclick = () => {
    disableBlocks(config, taskGenC)
    resetBtn.disabled = true
    confirmBtn.disabled = true;
    let prevs = [ aliceLearn.length, aliceGen,length, bobLearn.length, bobGen.length ].reduce((a, b) => a + b, 0)
    trialData.result[prevs+i] = '0'+getCurrentSelection(config, taskGenC)
    console.log(trialData)
    if (mode!=='dev') {
      const nextDiv = (i === bobGen.length-1)? '': `${taskGenC}-box-${i+2}`;
      showNext(nextDiv);
    }
  }
}
