import "./styles.scss"

import { basicSetup } from "codemirror"
import { EditorView, keymap } from "@codemirror/view"
import { indentWithTab } from "@codemirror/commands"
import { indentUnit } from "@codemirror/language"
import { python } from "@codemirror/lang-python"
import * as bootstrap from 'bootstrap'


let editor = new EditorView({
    doc: 'Loading...',
    extensions: [basicSetup, keymap.of([indentWithTab]), indentUnit.of("    "), python()],
    parent: document.getElementById("main-editor"),
})

var robotTemplate = document.getElementById("robot-template")

function drawRobot(ctx, state) {
    ctx.canvas.width = ctx.canvas.clientWidth
    ctx.canvas.height = ctx.canvas.clientHeight

    // with/height unit of the canvas
    let u = ctx.canvas.width

    let angleOffset = Math.PI * 1 / 32

    // put orgin at middle
    ctx.translate(u / 2, u / 2)

    // body
    ctx.beginPath()
    ctx.arc(0, 0, u / 2.3, 0, Math.PI * 2)
    ctx.fillStyle = "#2f822b"
    ctx.fill()
    ctx.stroke()

    // bumper left
    ctx.strokeStyle = (state.leftBumber) ? "#dd3131" : "#000000"
    ctx.lineWidth = (state.leftBumber) ? 3 : 1
    ctx.beginPath()
    ctx.arc(0, 0, u / 2.1, Math.PI + angleOffset, Math.PI * 4 / 3 - angleOffset)
    ctx.stroke()

    // bumper front
    ctx.strokeStyle = (state.frontBumper) ? "#dd3131" : "#000000"
    ctx.lineWidth = (state.frontBumper) ? 3 : 1
    ctx.beginPath()
    ctx.arc(0, 0, u / 2.1, Math.PI * 4 / 3 + angleOffset, Math.PI * 5 / 3 - angleOffset)
    ctx.stroke()

    // bumper right
    ctx.strokeStyle = (state.rightBumper) ? "#dd3131" : "#000000"
    ctx.lineWidth = (state.rightBumper) ? 3 : 1
    ctx.beginPath()
    ctx.arc(0, 0, u / 2.1, -Math.PI * 1 / 3 + angleOffset, 0 - angleOffset)
    ctx.stroke()

    // bumper back
    ctx.strokeStyle = (state.backBumper) ? "#dd3131" : "#000000"
    ctx.lineWidth = (state.backBumper) ? 3 : 1
    ctx.beginPath()
    ctx.arc(0, 0, u / 2.1, angleOffset, Math.PI - angleOffset)
    ctx.stroke()

    ctx.strokeStyle = "#000000"
    ctx.lineWidth = 1

    // motor height and width
    let mh = u / 10
    let mw = u / 5

    let motorpath = new Path2D()
    motorpath.moveTo(0 + u / 24, +mh / 2)
    motorpath.lineTo(0 + mw, +mh / 2)
    motorpath.lineTo(0 + mw, -mh / 2)
    motorpath.lineTo(0 + u / 24, -mh / 2)
    motorpath.lineTo(0 + u / 24, -mh / 4)
    motorpath.lineTo(0, -mh / 4)
    motorpath.lineTo(0, +mh / 4)
    motorpath.lineTo(0 + u / 24, +mh / 4)
    motorpath.closePath()

    // motor left
    ctx.save()
    ctx.translate(-u * 0.4, 0)
    ctx.save()
    ctx.clip(motorpath)
    ctx.fillStyle = "#ffffff"
    ctx.fill(motorpath)
    ctx.fillStyle = "#cc8a33"
    ctx.fillRect(0, mh / 2, u, -mh * state.leftMotor / 255)
    ctx.restore()
    ctx.stroke(motorpath)
    ctx.restore()

    // motor right
    ctx.save()
    ctx.scale(-1, 1)
    ctx.translate(-u * 0.4, 0)
    ctx.save()
    ctx.clip(motorpath)
    ctx.fillStyle = "#ffffff"
    ctx.fill(motorpath)
    ctx.fillStyle = "#cc8a33"
    ctx.fillRect(0, mh / 2, u, -mh * state.rightMotor / 255)
    ctx.restore()
    ctx.stroke(motorpath)
    ctx.restore()

    ctx.strokeStyle = "#ffffff"

    // LED size
    let ls = u / 8
    let ledpath = new Path2D()
    ledpath.moveTo(ls / 2, ls / 2)
    ledpath.lineTo(ls / 2, -ls / 2)
    ledpath.lineTo(-ls / 2, -ls / 2)
    ledpath.lineTo(-ls / 2, ls / 2)
    ledpath.closePath()

    // coms led
    ctx.fillStyle = "#" + (state.comsLED).toString(16).padStart(6, '0')
    ctx.fill(ledpath)
    ctx.stroke(ledpath)

    // status led
    ctx.save()
    ctx.translate(u / 5, u / 5)
    ctx.fillStyle = "#" + (state.statusLED).toString(16).padStart(6, '0')
    ctx.fill(ledpath)
    ctx.stroke(ledpath)
    ctx.restore()

    // color sensor size
    let csl = u / 10
    let cspath = new Path2D()
    cspath.moveTo(csl / 2, csl / 4)
    cspath.lineTo(csl / 2, -csl / 4)
    cspath.lineTo(-csl / 2, -csl / 4)
    cspath.lineTo(-csl / 2, csl / 4)
    cspath.closePath()

    // left color sensor
    ctx.save()
    ctx.translate(-u / 12, -u / 3)
    ctx.fillStyle = "#" + (state.leftSensor).toString(16).padStart(6, '0')
    ctx.fill(cspath)
    ctx.stroke(cspath)
    ctx.restore()

    // right color sensor
    ctx.save()
    ctx.translate(u / 12, -u / 3)
    ctx.fillStyle = "#" + (state.rightSensor).toString(16).padStart(6, '0')
    ctx.fill(cspath)
    ctx.stroke(cspath)
    ctx.restore()

    // sensor parabola
    ctx.fillStyle = "#adadad"
    ctx.beginPath()
    // ctx.arc(0, -u / 4, u/6, Math.PI*1/4, Math.PI*3/4)
    ctx.moveTo(u / 4, -u / 3.5)
    ctx.quadraticCurveTo(u / 6, -u / 5.5, 0, -u / 5.5)
    ctx.quadraticCurveTo(-u / 6, -u / 5.5, -u / 4, -u / 3.5)
    ctx.closePath()
    ctx.fill()
}

function updateRobot(state) {
    let robotcard = document.getElementById(`robot-${state.id}`)
    if (!robotcard) {
        let robotcardFragment = robotTemplate.content.cloneNode(true)
        robotcard = robotcardFragment.children[0]
        robotcard.setAttribute("id", `robot-${state.id}`)
        robotcard.getElementsByClassName("robot-name")[0].innerHTML = state.name
        document.getElementById("robotcard-container").appendChild(robotcardFragment)
    }

    let statustag = robotcard.getElementsByClassName("robot-status")[0]
    statustag.classList.remove("text-bg-success", "text-bg-warning", "text-bg-danger")
    statustag.innerHTML = state.status
    switch (state.status) {
        case "Running":
            statustag.classList.add("text-bg-success")
            break
        case "Stopped":
            statustag.classList.add("text-bg-warning")
            break
        case "Experiment error":
        case "Experiment exited":
            statustag.classList.add("text-bg-danger")
            break
        default:
            statustag.classList.add("text-bg-secondary")
    }
    let d = new Date(state.lastContact)
    robotcard.getElementsByClassName("robot-lastcontact")[0].innerHTML = d.toISOString()

    // drawRobot(robotcard.getElementsByClassName("robotcanvas")[0].getContext("2d"), state)
}

function refreshState() {
    let button = document.getElementById("action-button")

    button.classList.remove("btn-success", "btn-danger")

    if (state.experiment_running) {
        button.classList.add("btn-danger")
        button.innerHTML = "Stop"
    } else {
        button.classList.add("btn-success")
        button.innerHTML = "Run"
    }

    let statusbadge = document.getElementById("status")
    statusbadge.classList.remove("text-bg-success", "text-bg-danger")
    statusbadge.innerHTML = (state.experiment_running) ? "Running" : "Stopped"
    statusbadge.classList.add((state.experiment_running) ? "text-bg-success" : "text-bg-danger")

    let updatedbadge = document.getElementById("updated")
    updatedbadge.classList.remove("text-bg-success", "text-bg-warning")
    let updated_bots = Object.values(robots).filter((r) => {return r.experiment_hash === state.experiment_hash}).length
    let total_bots = Object.values(robots).length
    updatedbadge.classList.add((total_bots === updated_bots) ? "text-bg-success" : "text-bg-warning")
    updatedbadge.innerHTML = `${updated_bots}/${total_bots}`
}

// updateRobot({
//     id: 1,
//     name: "Bingus",
//     status: "Running",
//     lastContact: "2023-02-19 00:00:00",
//     leftBumber: true,
//     frontBumper: false,
//     rightBumper: false,
//     backBumper: false,
//     leftMotor: 128,
//     rightMotor: 200,
//     comsLED: 0x00ff00,
//     statusLED: 0xff0000,
//     leftSensor: 0x0000ff,
//     rightSensor: 0x0000ff,
// })

let robots = {}
let state = {}

const protocol = (location.protocol === 'https:') ? 'wss://' : 'ws://'
const host = location.hostname
const port = (location.port) ? `:${location.port}` : ''

let ws = new WebSocket(`${protocol}${host}${port}/user_ws`)

ws.onopen = function (event) {
    console.log("Websocket connected")
}

ws.onclose = function (event) {
    // set background color to red to alert about ws failing
    document.getRootNode().children[0].children[1].style = "background-color: rgb(255, 128, 128) !important"
}

ws.onmessage = function (event) {
    const message = JSON.parse(event.data)
    console.log(message)
    switch (message.type) {
        case 'init':
            editor.dispatch({ changes: { from: 0, to: editor.state.doc.length, insert: message["code"] } })
            break
        case 'telemetry':
            robots[message.name] = {
                id: message.name,
                name: message.name,
                status: { 2: "Running", 3: "Stopped", 4: "Experiment error", 5: "Experiment exited" }[message.state],
                experiment_hash: message.experiment_hash,
                lastContact: Date.now(),
                leftBumber: true,
                frontBumper: false,
                rightBumper: false,
                backBumper: false,
                leftMotor: 128,
                rightMotor: 200,
                comsLED: 0x00ff00,
                statusLED: 0xff0000,
                leftSensor: 0x0000ff,
                rightSensor: 0x0000ff,
            }
            updateRobot(robots[message.name])
            refreshState()
            break
        case 'state':
            state.experiment_running = message.experiment_running
            state.experiment_hash = message.experiment_hash
            refreshState()
            break
        default:
            console.error('unknown message type recieved', message)
    }
}

window.onbeforeunload = function () {
    // prevent the screen from flashing red
    ws.onclose = function () { }
    ws.close()
}

document.getElementById("upload-button").addEventListener("click", function () {
    ws.send(JSON.stringify({
        type: "upload",
        filename: document.getElementById("progname").value,
        code: editor.state.doc.toString(),
    }))
})

document.getElementById("action-button").addEventListener("click", function () {
    if (state.experiment_running) {
        ws.send(JSON.stringify({
            type: "stop",
        }))
    } else {
        ws.send(JSON.stringify({
            type: "run",
        }))
    }
})