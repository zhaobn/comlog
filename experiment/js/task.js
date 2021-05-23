
const mode = '' // '' for production, 'dev' for development, 'flask' for flask-app

/** Pick a condition */
const cond = 'row'
const cond_dict = {
  'row': [1,2,3],
  'col': [1,4,7],
  'ldg': [1,5,9],
  'rdg': [3,5,7],
}
taskConfigs = config.filter(c => c.phase === 'tab' & cond_dict[cond].indexOf(c.trial) > -1 );
let learnClicked = Array(taskConfigs.length).fill(0);
console.log(cond)

// Generate learning frame
learnDivPrefix = 'task-obs-training'
coreLearnDiv = document.getElementById(learnDivPrefix)
for(let i = 0; i < taskConfigs.length; i++ ) {
  let { _, trial, agent, recipient, result } = taskConfigs[i];
  let config = { trial: i+1, taskId: trial, agent, recipient, result }

  let trialId = config.trial;
  let display = (mode==='dev'|i===0)? 'flex': 'none';

  let box = createCustomElement("div", "box", `${learnDivPrefix}-box-${trialId}`);
  let taskBox = createCustomElement("div", "task-box", `${learnDivPrefix}-taskbox-${trialId}`);

  let taskNum = createText('h2', `${trialId}/${taskConfigs.length}`);
  taskBox.append(taskNum);

  let displayBox = createCustomElement("div", "display-box", `${learnDivPrefix}-displaybox-${trialId}`);

  let displayMain = createCustomElement("div", "display-main", `${learnDivPrefix}-displaymain-${trialId}`);
  displayMain = createInitStones(config, displayMain);

  let displayHist = createCustomElement("div", "display-hist", `${learnDivPrefix}-displayhist-${trialId}`);
  displayHist = createInitHistory(config, displayHist)
  displayHist.style.opacity = 0

  displayBox.append(displayMain)
  displayBox.append(displayHist)

  const buttonGroup = createCustomElement("div", "button-group-vc", `learn${trialId}`);
  buttonGroup.append(createBtn(`${learnDivPrefix}-test-btn-${trialId}`, "Test", true));
  buttonGroup.append(createBtn(`${learnDivPrefix}-next-btn-${trialId}`, "Next", false));

  taskBox.append(displayBox);
  taskBox.append(buttonGroup);
  box.append(taskBox);
  box.style.display = display;
  coreLearnDiv.append(box);

  /** Button functionalities */
  const playBtn = document.getElementById(`${learnDivPrefix}-test-btn-${trialId}`);
  const nextBtn = document.getElementById(`${learnDivPrefix}-next-btn-${trialId}`);

  playBtn.onclick = () => {
    playBtn.disabled = true;
    if (learnClicked[i] > 0) {
      clearElement(`learn${config.trial}-agent-div`)
      clearElement(`learn${config.trial}-recipient-blocks-all`)
      createInitStones(config, displayMain)
      displayHist.style.opacity = 0
    }
    playEffects(config);
    setTimeout(() => {
      nextBtn.disabled = false;
      playBtn.disabled = false;
      playBtn.innerText = 'Test again'
      // boxWrapper.style.display = 'flex';
    }, 2000);
    learnClicked[i] += 1;
  }
  nextBtn.onclick = () => {
    nextBtn.disabled = true;
    if (i <= taskConfigs.length-1) {
      showNext(`task-obs-training-box-${trialId+1}`, 'flex')
    }
    // const nextDiv = (i === taskConfigs.length-1)? '': `task-obs-training-box-${i+2}`;
    // (mode !== 'dev')? hide(`box-${trialId}`): null;
    // showNext(nextDiv, 'flex');
  }

}

// Generate agent stone

// Generate recipient stone

// Generate result stone

// Add animation

// Try gen task selection
