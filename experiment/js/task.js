
const mode = 'test' // '', 'dev', 'test', 'flask'

/** Pick a condition */
const cond = 'easy'
console.log(`${mode} mode; condition ${cond}.`);


const start_time = Date.now();
let start_task_time = 0;


/** Prep data */
const exp_conds = {
  'easy': {
    'alice': {
      'learn': [5,6,7],
      'gen': [8],
    },
    'bob': {
      'learn': [2,6,10],
      'gen': [14],
    }
  },
  'hard': {
    'alice': {
      'learn': [1,2,3],
      'gen': [4],
    },
    'bob': {
      'learn': [4,6,13],
      'gen': [11],
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
     playBtn.disabled = true;
     let nextDiv = (i === aliceLearn.length-1)? taskInputA: `${taskTrainA}-box-${i+2}`;
     showNext(nextDiv);
   }
}

// Free response
(mode === 'dev')? document.getElementById(taskInputA).style.display = 'flex': null;
document.getElementById(taskInputA).append(createInputForm(taskInputA))

const aliceInputForm = document.getElementById(`${taskInputA}-input-form`)
let aliceOkBtn = document.getElementById(`${taskInputA}-input-submit-btn`)
aliceInputForm.onchange = () => isFilled(`${taskInputA}-input-form`)? aliceOkBtn.disabled = false: null;
aliceOkBtn.onclick = () => {
  let inputs = aliceInputForm.elements;
  Object.keys(inputs).forEach(id => subjectData[inputs[id].name] = inputs[id].value);
  aliceOkBtn.disabled = true;
  disableFormInputs(`${taskInputA}-input-form`);
  // console.log(subjectData)
  hide('task-input-a-button-group-vc')
  showNext(taskGenA, 'block')
}

// Generate gen tasks
// (mode === 'dev')? document.getElementById(taskGenA).style.display = 'block': null;
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
    trialData.result[aliceLearn.length+i] = '0|'+getCurrentSelection(config, taskGenA)
    // console.log(trialData)
    if (i < aliceGen.length-1) {
      hide(`${taskGenA}-box-${i+1}`)
      showNext(`${taskGenA}-box-${i+2}`);
    } else {
      hide(taskCoverA)
      hide(taskTrainA)
      hide(taskInputA)
      hide(taskGenA)
      showNext('task-bob', 'block');
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
    playBtn.disabled = true;
    let nextDiv = (i === bobLearn.length-1)? taskInputB: `${taskTrainB}-box-${i+2}`;
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
  // console.log(subjectData)
  hide('task-input-b-button-group-vc')
  showNext(taskGenB, 'block')
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
    let prevs = [ aliceLearn.length, aliceGen.length, bobLearn.length ].reduce((a, b) => a + b, 0)
    trialData.result[prevs+i] = '0|'+getCurrentSelection(config, taskGenC)
    if (i < aliceGen.length-1) {
      hide(`${taskGenB}-box-${i+1}`);
      showNext(`${taskGenB}-box-${i+2}`);
    } else {
      hide(taskCoverB)
      hide(taskTrainB)
      hide(taskInputB)
      hide(taskGenB)
      showNext('task-comp', 'block');
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
  // console.log(subjectData)
  hide('task-input-c-button-group-vc')
  showNext(taskGenC, 'block')
}

// Generate gen tasks
for(let i = 0; i < genConfigs.length; i++ ) {
  let config = genConfigs[i]
  // console.log(config)
  document.getElementById(taskGenC).append(createGenTask(taskGenC, config, genConfigs.length))
  if (mode !== 'dev' && i > 0) {
    document.getElementById(`${taskGenC}-box-${i+1}`).style.display = 'none'
  }


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
    let prevs = [ aliceLearn.length, aliceGen.length, bobLearn.length, bobGen.length ].reduce((a, b) => a + b, 0)
    trialData.result[prevs+i] = '0|'+getCurrentSelection(config, taskGenC)
    // console.log(trialData)
    hide(`${taskGenC}-box-${i+1}`)
    if (i < genConfigs.length-1) {
      showNext(`${taskGenC}-box-${i+2}`, 'flex', false);
    } else {
      hide(taskCoverC)
      hide(taskTrainC)
      hide(taskInputC)
      hide(taskGenC)
      showNext('debrief', 'block');
    }
  }
}


// Instruction buttons
// const checkScrollHeight = (text, btn) => ((text.scrollTop + text.offsetHeight) >= text.scrollHeight) ? btn.disabled = false : null;
const descNextBtn = document.getElementById('desc-next-btn')

// const instructionText = document.getElementById("instruction-text");
// instructionText.addEventListener("scroll", () => checkScrollHeight(instructionText, descNextBtn), false);
descNextBtn.onclick = () => {
  hide('instruction')
  showNext('comprehension', 'block')
}



// Quiz
const checkBtn = document.getElementById('check-btn');
const checks = [ 'check1', 'check2', 'check3', 'check4', 'check5', 'check6' ];
const answers = [ true, false, true, false, true, true ];

const passBtn = document.getElementById('pass-btn');
const retryBtn = document.getElementById('retry-btn');

checkBtn.onclick = () => {
  checkBtn.style.display = 'none';
  let inputs = [];
  checks.map(check => {
    const vals = document.getElementsByName(check);
    inputs.push(vals[0].checked);
  });
  const pass = (inputs.join('') === answers.join(''));
  if (pass) {
    showNext('pass', 'block')
  } else {
    showNext('retry', 'block')
  }
}

passBtn.onclick = () => {
  start_task_time = Date.now();
  hide("pass");
  hide("comprehension");
  showNext("task-alice", "block");
};
retryBtn.onclick = () => {
  hide("retry");
  hide("comprehension");
  showNext("instruction", "block")
  checkBtn.style.display = 'flex';
};

document.getElementById('prequiz').onchange = () => compIsFilled() ? checkBtn.disabled = false : null;


// Bebrief
const doneBtn = document.getElementById('done-btn');
const debriefForm = document.getElementById('postquiz');

debriefForm.onchange = () => {
  isFilled('postquiz')? doneBtn.disabled = false: null;
}
doneBtn.onclick = () => {
  let inputs = debriefForm.elements;
  Object.keys(inputs).forEach(id => subjectData[inputs[id].name] = inputs[id].value);

  const end_time = new Date();
  let token = generateToken(8);

  let clientData = {};
  clientData.subject = subjectData;
  clientData.subject.condition = cond;
  clientData.subject.date = formatDates(end_time, 'date');
  clientData.subject.time = formatDates(end_time, 'time');
  clientData.subject.instructions_duration = start_task_time - start_time,
  clientData.subject.task_duration = end_time - start_task_time,
  clientData.subject.token = token;
  clientData.trials = trialData;

  // /** Give feedback */
  // const truths = genConfigs.map(c => c[4])
  // const predicted = trialData.result.slice(learnConfigs.length,);
  // let correct = 0;
  // truths.forEach((t, i) => (t===predicted[i])? correct+=1: null);
  // clientData.subject.correct = correct;

  if (mode === 'flask') {
    fetch(root_string, {
        method: 'POST',
        body: JSON.stringify(clientData),
    })
    .then(() => showCompletion(token))
    .catch((error) => console.log(error));
  } else {
    showCompletion(token);
    // console.log(clientData);
    download(JSON.stringify(clientData), 'data.txt', '"text/csv"');
  }
};



// Dev buttons
const devSkipIntro = document.getElementById('dev-skip-intro')
devSkipIntro.style.display = (mode==='dev'|mode==='test')? 'block': 'none'
devSkipIntro.onclick = () => {
  hide('instruction')
  hide('comprehension')
  hide('pass')
  hide('retry')
  showNext('task-alice', 'block')
}

const devSkipAlice = document.getElementById('dev-skip-alice')
devSkipAlice.style.display = (mode==='dev'|mode==='test')? 'block': 'none'
devSkipAlice.onclick = () => {
  hide(taskCoverA)
  hide(taskTrainA)
  hide(taskInputA)
  hide(taskGenA)
  showNext('task-bob', 'block')
}

const devSkipBob = document.getElementById('dev-skip-bob')
devSkipBob.style.display = (mode==='dev'|mode==='test')? 'block': 'none'
devSkipBob.onclick = () => {
  hide(taskCoverB)
  hide(taskTrainB)
  hide(taskInputB)
  hide(taskGenB)
  showNext('task-comp', 'block')
}


const devSkipComp = document.getElementById('dev-skip-comp')
devSkipComp.style.display = (mode==='dev'|mode==='test')? 'block': 'none'
devSkipComp.onclick = () => {
  hide(taskCoverC)
  hide(taskTrainC)
  hide(taskInputC)
  hide(taskGenC)
  showNext('debrief', 'block')
}
