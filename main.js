const canvas = document.getElementById('canvas');
const ctxMain = canvas.getContext('2d');
const canvasWorld = document.createElement('canvas')
canvasWorld.width = canvas.width
canvasWorld.height = canvas.height
const ctxWorld = canvasWorld.getContext('2d')
const canvasPheroRed = document.createElement('canvas')
canvasPheroRed.width = canvas.width
canvasPheroRed.height = canvas.height
const ctxPheroRed = canvasPheroRed.getContext('2d')

const canvasPheroGreen = document.createElement('canvas')
canvasPheroGreen.width = canvas.width
canvasPheroGreen.height = canvas.height
const ctxPheroGreen = canvasPheroGreen.getContext('2d')

const canvasPheroBlue = document.createElement('canvas')
canvasPheroBlue.width = canvas.width
canvasPheroBlue.height = canvas.height
const ctxPheroBlue = canvasPheroBlue.getContext('2d')

const canvasPhero = document.createElement('canvas')
canvasPhero.width = canvas.width
canvasPhero.height = canvas.height
const ctxPhero = canvasPhero.getContext('2d')


const a = 2 * Math.PI / 6;
const margin = 30

let games = []
let rounds = []

await fetch('./game-list.txt')
    .then(response => response.text())
    .then(contents => {
        const selectElement = document.getElementById('game-selector')
        const gamenames = contents.split("\n")
        gamenames.forEach( game => {
            const optionElement = document.createElement('option');
            optionElement.value = game
            optionElement.className = "text-center"
            games.push(optionElement.value)
            optionElement.textContent = game
            selectElement.append(optionElement)
        })
    })
    .catch(error => console.log(error))



let current_game = ""
let current_round = ""
async function select_game(game) {
    current_game = game
    await fetch('./'+ game +'/rounds.txt')
    .then(response => response.text())
    .then(contents => {
        const selectElement = document.getElementById('round-selector')
        const roundnames = contents.split("\n")
        selectElement.innerHTML=""
        rounds = []
        roundnames.forEach( game => {
            const optionElement = document.createElement('option');
            optionElement.value = rounds.length
            optionElement.className = "text-center"
            rounds.push(game + ".json")
            optionElement.textContent = game
            selectElement.append(optionElement)
        })
        current_round = 0
    })
    .catch(error => console.log(error))
}

await select_game(games[0])


async function load_game(game) {
    await select_game(game)
    await reload_file()
}

window.load_game = load_game

async function load_round(round) {
    current_round = round
    await reload_file()
}

window.load_round = load_round


async function next_game() {
    current_round = Math.min(rounds.length-1,current_round+1)
    await reload_file()
}
window.next_game = next_game

async function previous_game() {
    current_round = Math.max(0,current_round-1)
    await reload_file()
}
window.previous_game = previous_game

let jsondata = await fetch('./'+current_game+'/' + rounds[current_round]).then((response)=> response.json())

let map = jsondata.world
let world_heigth = map.length
let world_width = map[0].length
let bases = jsondata.bases
let units = jsondata.units
let phero = jsondata.phero
let row = map.length
let col = map[0].length
let winner = jsondata.winner
let vision
let smell
let sensor
let data_out = jsondata.data_out
if (data_out) {
    console.log("data_out activated")
    vision = jsondata.vision
    smell = jsondata.smell
    sensor = jsondata.sensor
}

const sqrt_3 = 1.732
let size_w = Math.floor((canvas.width - 2*margin)/((((row-1)/2)+2*col)))
let size_h = Math.floor((canvas.height -2*margin)/(0.5 + 1.5*row))
let size = Math.min(size_w,size_h)
let offset_x = (canvas.width -(sqrt_3*((row/2)+col))*size)/2 + 0.75*sqrt_3*size
let offset_y = (canvas.height-(0.5 + 1.5*row)*size)/2 + size
let d_horizontal = sqrt_3*size
let d_vertical = 3/2*size

let base_outer_radius = size * 1.2
let base_inner_radius = size * 0.9
let base_center_ring_radius = size * 0.7
let base_center_radius = size * 0.5

let unit_outer_radius = size / 1.6
let unit_inner_radius = size / 2.1



let step = 0
async function reload_file() {
    await fetch('./'+ current_game +'/' + rounds[current_round]).then((response)=> response.json()).then(
       (jsondata) => {
           //reasign all global Variables
           map = jsondata.world
           world_heigth = map.length
           world_width = map[0].length
           bases = jsondata.bases
           units = jsondata.units
           phero = jsondata.phero
           row = map.length
           col = map[0].length
           winner = jsondata.winner
           data_out = jsondata.data_out
           if (data_out) {
               console.log("data_out activated")
               vision = jsondata.vision
               smell = jsondata.smell
               sensor = jsondata.sensor
           }

           size_w = Math.floor((canvas.width - 2*margin)/((((row-1)/2)+2*col)))
           size_h = Math.floor((canvas.height -2*margin)/(0.5 + 1.5*row))
           size = Math.min(size_w,size_h)
           offset_x = (canvas.width -(sqrt_3*((row/2)+col))*size)/2 + 0.75*sqrt_3*size
           offset_y = (canvas.height-(0.5 + 1.5*row)*size)/2 + size
           d_horizontal = sqrt_3*size
           d_vertical = 3/2*size

           base_outer_radius = size * 1.2
           base_inner_radius = size * 0.9
           base_center_ring_radius = size * 0.7
           base_center_radius = size * 0.5

           unit_outer_radius = size / 1.6
           unit_inner_radius = size / 2.1
       }
    )
    step = 0
    init()
}


function init() {
    ctxMain.font = "30px Arial"
    ctxWorld.fillStyle = ("#44AAFF")
    ctxWorld.fillRect(0, 0, canvas.width, canvas.height);
    ctxWorld.fillStyle =("#FFFFFF")
    for(var i = 0; i < map.length; i++) {
        for(var j = 0; j < map[i].length; j++) {
            if (map[i][j] == 0) {
                drawHexagon(ctxWorld,i,j,size,"#FFFFFF")
            } else if (map[i][j] == 1) {
                drawHexagon(ctxWorld,i,j,size, "purple")
            }
        }
    }
    test()
    update()
}

function update() {
    ctxMain.clearRect(0,0,canvas.width,canvas.height)
    ctxMain.drawImage(canvasWorld,0,0)
    draw_pheromones()
    for (var i=0; i<units[step].length; i++) {
        drawUnit(ctxMain, units[step][i][0], units[step][i][1], units[step][i][2], units[step][i][3])
    }
    for(var i = 0; i < bases.length; i++) {
        drawBase(ctxMain, bases[i][0],bases[i][1],bases[i][2])
    }
    ctxMain.fillText(step.toString(), canvas.width-100,50)
    if (step == units.length-1){
        let text
        if (winner == "#FF0000") {
            text = "Red Won"
        } else if (winner == "#0000FF") {
            text = "Blue Won"
        } else {
            text = "Tie"
        }
        ctxMain.fillText(text,30, canvas.height-20)
    }
    if (data_out) {
        draw_data()
    }
    document.dataURL = canvas.toDataURL()
}


let directions = ["BL ","FL ","F   ","FR ","BR ","B   "]
function draw_data() {
    ctxMain.font = "20px Arial"
    ctxMain.fillText("smell:",10,30)

    for (let i= 0; i < smell[step].length;i++) {
        let smellstring = directions[i] + "["
        smellstring += " ("+ smell[step][i][0].toString() + ")"
        smellstring += " ("+ smell[step][i][1].toString() + ")"
        smellstring += "]"
        ctxMain.fillText(smellstring,10,50+i*20)
    }

    ctxMain.fillText("vision:",10,50+6*20)
    for (let i= 0; i < vision[step].length;i++) {
        let visionstring = directions[i] + "["
        visionstring +=  vision[step][i].toFixed(2)
        visionstring += "]"
        ctxMain.fillText(visionstring,10,50+(i+7)*20)
    }

    ctxMain.fillText("sense:",100,50+6*20)
    for (let i= 0; i < vision[step].length;i++) {
        let sensestring = directions[i] + "["
        sensestring +=  sensor[step][i].toString()
        sensestring += "]"
        ctxMain.fillText(sensestring,100,50+(i+7)*20)
    }




    //ctxMain.fillText(arrayToString(vision[step]),10,30)
    //ctxMain.fillText(arrayToString(sensor[step]),10,50)
    ctxMain.font = "30px Arial"
}


function draw_pheromones() {
    //RED
    ctxPhero.globalCompositeOperation = "source-over"
    ctxPhero.clearRect(0,0,canvasPhero.width,canvasPhero.height)
    for (var i = 0; i < world_heigth;i++) {
        for (var j = 0; j < world_width; j++) {
            if (phero[step][0][i][j] > 0) {
                drawHexagon(ctxPhero,i,j,size,`rgba(
                    ${255},
                    ${0},
                    ${0},
                    ${phero[step][0][i][j]/50})`,false)
            }
        }
    }
    ctxPhero.clearRect(0,0,ctxPhero.width,ctxPhero.height)
    ctxPhero.globalCompositeOperation = "source-in"
    ctxPhero.drawImage(canvasPheroRed,0,0)
    ctxMain.drawImage(canvasPhero,0,0)
    //GREEN
    ctxPhero.globalCompositeOperation = "source-over"
    ctxPhero.clearRect(0,0,canvasPhero.width,canvasPhero.height)
    for (var i = 0; i < world_heigth;i++) {
        for (var j = 0; j < world_width; j++) {
            if (phero[step][1][i][j] > 0) {
                drawHexagon(ctxPhero,i,j,size,`rgba(
                    ${0},
                    ${255},
                    ${0},
                    ${phero[step][1][i][j]/50})`,false)
            }
        }
    }
    ctxPhero.globalCompositeOperation = "source-in"
    ctxPhero.drawImage(canvasPheroGreen,0,0)
    ctxMain.drawImage(canvasPhero,0,0)
    //BLUE
    ctxPhero.globalCompositeOperation = "source-over"
    ctxPhero.clearRect(0,0,canvasPhero.width,canvasPhero.height)
    for (var i = 0; i < world_heigth;i++) {
        for (var j = 0; j < world_width; j++) {
            if (phero[step][2][i][j] > 0) {
                drawHexagon(ctxPhero,i,j,size,`rgba(
                    ${0},
                    ${0},
                    ${255},
                    ${phero[step][2][i][j]/50})`,false)
            }
        }
    }
    ctxPhero.globalCompositeOperation = "source-in"
    ctxPhero.drawImage(canvasPheroBlue,0,0)
    ctxMain.drawImage(canvasPhero,0,0)
}

function test() {
    for (var i = 0; i < canvas.width; i++) {
        for (var j = 0; j < canvas.height; j++) {
            var alpha = 0
            var val = Math.floor(Math.random()*255)
            if (val <= 70){
                alpha = (val/70)*255
                ctxPheroRed.fillStyle = `rgb(
                    ${255},
                    ${0},
                    ${0},
                    ${alpha})`;
                ctxPheroRed.fillRect(i,j,1,1)
            } else if (val <=140) {
                alpha = (val-70)/70*255
                ctxPheroGreen.fillStyle = `rgb(
                    ${0},
                    ${255},
                    ${0},
                    ${alpha})`;
                ctxPheroGreen.fillRect(i,j,1,1)
            } else if (val <=210) {
                alpha = (val-140)/70*255
                ctxPheroBlue.fillStyle = `rgb(
                    ${0},
                    ${0},
                    ${255},
                    ${alpha})`;
                ctxPheroBlue.fillRect(i,j,1,1)
            }
        }
    }
}
init()

function drawHexagon(ctx,x, y,radius,color,stroke=true) {
  ctx.beginPath();
  for (var i = 0; i < 6; i++) {
    ctx.lineTo(offset_x + y*d_horizontal +x/2*d_horizontal + radius * Math.cos(a * i-a/2), offset_y + x*d_vertical + radius * Math.sin(a * i-a/2));
  }
  ctx.closePath();
  if (stroke) {
      ctx.stroke();
  }
  ctx.save()
  ctx.fillStyle = color
  ctx.fill();
  ctx.restore()
}

function drawCircle(ctx, x, y, radius, color) {
    ctx.beginPath()
    ctx.arc(offset_x + y*d_horizontal +x/2*d_horizontal, offset_y + x*d_vertical , radius, 0, 2 * Math.PI, false)
    ctx.stroke()
    ctx.save()
    ctx.fillStyle = color
    ctx.fill()
    ctx.restore()
}


function deg_to_rad(deg) {
    return deg/360 * 2*Math.PI
}
function drawBase(ctx,x,y,color) {
    ctx.beginPath();
    for (var i = 0; i < 6; i++) {
        ctx.lineTo(offset_x + y*d_horizontal +x/2*d_horizontal + base_outer_radius * Math.cos(a * i + deg_to_rad(5) - a/2), offset_y + x*d_vertical + base_outer_radius * Math.sin(a * i + deg_to_rad(5) - a/2));
        ctx.lineTo(offset_x + y*d_horizontal +x/2*d_horizontal + base_inner_radius * Math.cos(a * i + deg_to_rad(13) -a/2), offset_y + x*d_vertical + base_inner_radius * Math.sin(a * i + deg_to_rad(13) -a/2));
        ctx.lineTo(offset_x + y*d_horizontal +x/2*d_horizontal + base_inner_radius * Math.cos(a * i + deg_to_rad(47) -a/2), offset_y + x*d_vertical + base_inner_radius * Math.sin(a * i + deg_to_rad(47) -a/2));
        ctx.lineTo(offset_x + y*d_horizontal +x/2*d_horizontal + base_outer_radius * Math.cos(a * i + deg_to_rad(55) -a/2), offset_y + x*d_vertical + base_outer_radius * Math.sin(a * i + deg_to_rad(55) -a/2));
    }
    ctx.closePath();
    ctx.stroke();
    ctx.save()
    ctx.fillStyle = "gray"
    ctx.fill();
    ctx.restore()
    drawCircle(ctx,x,y,base_center_ring_radius,"black")
    drawCircle(ctx,x,y,base_center_radius,color)
}

function drawUnit(ctx,x,y,color,dir) {
    drawHexagon(ctx,x,y,unit_outer_radius,"gray")
    drawHexagon(ctx,x,y,unit_inner_radius, color)
    ctx.beginPath();
    ctx.lineTo(offset_x + y*d_horizontal +x/2*d_horizontal + unit_outer_radius * Math.cos(a * dir -a/2), offset_y + x*d_vertical + unit_outer_radius * Math.sin(a * dir -a/2));
    ctx.lineTo(offset_x + y*d_horizontal +x/2*d_horizontal + unit_inner_radius * Math.cos(a * dir -a/2), offset_y + x*d_vertical + unit_inner_radius * Math.sin(a * dir -a/2));
    ctx.lineTo(offset_x + y*d_horizontal +x/2*d_horizontal + unit_inner_radius * Math.cos(a * (dir+1) -a/2), offset_y + x*d_vertical + unit_inner_radius * Math.sin(a * (dir+1) -a/2));
    ctx.lineTo(offset_x + y*d_horizontal +x/2*d_horizontal + unit_outer_radius * Math.cos(a * (dir+1) -a/2), offset_y + x*d_vertical + unit_outer_radius * Math.sin(a * (dir+1) -a/2));
    ctx.stroke();
    ctx.save()
    ctx.fillStyle = "black"
    ctx.fill();
    ctx.restore()
}


export function add_step(s) {
    step += s
    if (step < 0) {
        step = 0
    }
    step %= units.length
    update()
}

window.add_step = add_step

var speed = 1000
export function set_speed(s) {
    speed = s
}
window.set_speed = set_speed

var running = false
function start() {
    if (running) {
        return
    }
    running = true
    _gogogo()
}
window.start = start
export function stop() {
    running = false
}
window.stop = stop

function _gogogo(){
    if (!running) {
        return
    }
    if (step == units.length-1) {
        running = false
        return;
    }
    add_step(1)
    setTimeout(_gogogo,speed)
}