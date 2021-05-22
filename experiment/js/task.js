
const mode = 'dev' // '' for production, 'dev' for development, 'flask' for flask-app

/** Pick a condition */
const cond = 'col'
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
  displayBox = createInitStones(config, displayBox);

  const buttonGroup = createCustomElement("div", "button-group-vc", `${display}-btns-${trialId}`);
  buttonGroup.append(createBtn(`${display}-btns-${trialId}-test`, "Test", true));
  buttonGroup.append(createBtn(`${display}-btns-${trialId}-next`, "Next", false));

  taskBox.append(displayBox);
  taskBox.append(buttonGroup);
  box.append(taskBox);
  box.style.display = display;
  coreLearnDiv.append(box);

  /** Button functionalities */
  const playBtn = document.getElementById(`flex-btns-${trialId}-test`);
  const nextBtn = document.getElementById(`flex-btns-${trialId}-next`);

  playBtn.onclick = () => {
    playBtn.disabled = true;
    if (learnClicked[i] > 0) {
      clearStones(config);
      createInitStones(config, displayBox)
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
  // nextBtn.onclick = () => {
  //   nextBtn.disabled = true;
  //   const nextDiv = (i === learnConfigs.length-1)? "core-learn-form-div": `box-learn-${padNum(i+2)}`;
  //   (mode !== 'dev')? hide(`box-${trialId}`): null;
  //   showNext(nextDiv, 'flex');
  // }

}

// Generate agent stone

// Generate recipient stone

// Generate result stone

// Add animation

// Try gen task selection
