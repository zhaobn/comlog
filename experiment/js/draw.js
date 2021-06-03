
let baseDiv = document.getElementById('test')

function createLineElement(x, y, length, angle) {
  var line = document.createElement("div");
  var styles = 'border: 2px solid green; '
             + 'width: ' + length + 'px; '
             + 'height: 0px; '
             + '-moz-transform: rotate(' + angle + 'rad); '
             + '-webkit-transform: rotate(' + angle + 'rad); '
             + '-o-transform: rotate(' + angle + 'rad); '
             + '-ms-transform: rotate(' + angle + 'rad); '
             + 'position: absolute; '
             + 'top: ' + y + 'px; '
             + 'left: ' + x + 'px; ';
  line.setAttribute('style', styles);
  return line;
}

function createLine(x1, y1, x2, y2) {
  var a = x1 - x2,
      b = y1 - y2,
      c = Math.sqrt(a * a + b * b);

  var sx = (x1 + x2) / 2,
      sy = (y1 + y2) / 2;

  var x = sx - c / 2,
      y = sy;

  var alpha = Math.PI - Math.atan2(-b, a);

  return createLineElement(x, y, c, alpha);
}

function getLinePos(divId, n) {

}

function getCenterLinePos(id) {
  let rect = {top: 0, bottom: 0, left: 0, right: 0};
  const pos = document.getElementById(id).getBoundingClientRect();
  rect.top = pos.top;
  rect.bottom = pos.bottom;
  rect.left = pos.left;
  rect.right = pos.right;
  return rect
}

baseDiv.append(createLine(100, 100, 200, 200));
baseDiv.append(createLine(210, 200, 100, 100));
console.log(getCenterLinePos('test'))
