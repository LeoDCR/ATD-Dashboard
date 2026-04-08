import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Window 2.15

ApplicationWindow {
    visible: true
    width: 800
    height: 480
    title: "Dashboard Perrón"
    color: "#000000"
    visibility: Window.FullScreen

    Rectangle {
        anchors.fill: parent
        color: "transparent"
        Text {
            id: speedText
            anchors.centerIn: parent
            text: backend ? backend.speed.toFixed(0) : "0"
            color: "#00FF00"
            font.pixelSize: 120
            font.bold: true
        }
        Text {
            anchors.top: speedText.bottom
            anchors.horizontalCenter: parent.horizontalCenter
            text: "KM/H"
            color: "#FFFFFF"
            font.pixelSize: 20
        }
        Text {
            anchors.left: parent.left
            anchors.verticalCenter: parent.verticalCenter
            anchors.leftMargin: 50
            text: (backend ? backend.rpm.toFixed(0) : "0") + "\nRPM"
            color: "#FFFF00"
            font.pixelSize: 40
        }
        Text {
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.margins: 40
            text: "TEMP: " + (backend ? backend.temp.toFixed(1) : "0") + "°C"
            color: "#FF5555"
            font.pixelSize: 30
        }
        Text {
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            anchors.margins: 40
            text: "BATT: " + (backend ? backend.batt.toFixed(1) : "0") + "V"
            color: "#55AAFF"
            font.pixelSize: 30
        }
    }
    Connections {
        target: backend
        function onSpeedChanged(val) { speedText.text = val.toFixed(0) }
    }
}