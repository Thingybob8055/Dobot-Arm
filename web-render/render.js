this.render_armcode = function(armcode_text) {
    project.activeLayer.removeChildren();
    paper.view.draw();
    var cur = new Point(50,50);
    var penDown = false;
    armcode_text.split("\n").forEach(function(line) {
        if (line==="u") {
            penDown = false;
        }
        else if (line==="d") {
            penDown = true;
        }
        else if (line.startsWith("m")) {
            var movCmd = line.split(",");
            if (movCmd.length != 3) return;
            var offset = new Point(parseFloat(movCmd[1])*4, parseFloat(movCmd[2])*4);
            if (penDown) {
                var end = cur+offset;
                var path = new Path.Line(cur, end);
                path.strokeColor = 'black';
                cur = end;
            }
            else {
                cur += offset;
            }
            
        }
        console.log(line);
    });
    var cur = new Point(0, 0);
};

// Create a circle shaped path with its center at the center
// of the view and a radius of 30:
var path = new Path.Circle({
    center: view.center,
    radius: 30,
    strokeColor: 'black'
});

function onResize(event) {
    // Whenever the window is resized, recenter the path:
    path.position = view.center;
}
paper.install(window.paperscript);