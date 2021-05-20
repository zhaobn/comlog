
const mode = '' // '' for production, 'dev' for development, 'flask' for flask-app

/** Pick a condition */
const cond = 'row'
const cond_dict = {
  'row': [1,2,3],
  'col': [1,4,7],
  'ldg': [1,5,9],
  'rdg': [3,5,7],
}
task_config = config.filter(c => c.phase === 'tab' & cond_dict[cond].indexOf(c.trial) > -1 );
console.log(cond)

// Generate learning frame

// Generate agent stone

// Generate recipient stone

// Generate result stone

// Add animation

// Try gen task selection
