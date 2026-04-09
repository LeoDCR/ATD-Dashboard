import QtQuick 2.15

import QtQuick.Window 2.15

import QtQuick.Controls 2.15

import QtQuick.Layouts 1.15

import QtQuick.Shapes 1.15



Window {

    id: root

    visible: true

    width: 800

    height: 480

    title: "Moto Dashboard"

    color: "#050505" // Casi negro para mejor contraste

    visibility: Window.FullScreen // Importante para EGLFS



    // --- PROPIEDADES (Simulando conexión con Python) ---

    // Estas son las que tu backend actualizará

    property real speedVal: 0     // km/h

    property real rpmVal: 0       // 0 a 12000

    property real tempVal: 85     // Grados C

    property real battVal: 12.4   // Voltios

    property string gearVal: "N"  // Marcha

    property bool leftTurn: false

    property bool rightTurn: false



    // Configuraciones máximas

    readonly property real maxRPM: 12000

    readonly property real redLineRPM: 10000



    // --- FUENTES ---

    FontLoader {

        id: mainFont

        // Asegúrate de tener este archivo o comenta esta línea

        source: "Orbitron-Bold.ttf" 

    }



    // --- LÓGICA DE SIMULACIÓN (Bórralo cuando conectes Python) ---

    Timer {

        interval: 50; running: true; repeat: true

        onTriggered: {

            // Simular RPM subiendo y bajando

            root.rpmVal = (Math.sin(Date.now() / 1000) + 1) * 5500 + 1000

            root.speedVal = Math.floor(root.rpmVal * 0.012)

            

            // Simular Marcha

            if(speedVal == 0) gearVal = "N"

            else if(speedVal < 20) gearVal = "1"

            else if(speedVal < 40) gearVal = "2"

            else gearVal = "3"



            // Simular Temperatura crítica

            root.tempVal = 80 + (Math.sin(Date.now() / 5000) * 25)

        }

    }



    // --- FONDO TÉCNICO (Grid) ---

    Item {

        anchors.fill: parent

        opacity: 0.2

        Repeater {

            model: 10

            Item {

                width: 1; height: parent.height

                x: parent.width / 10 * index

                Rectangle { anchors.fill: parent; color: "#00FFFF" }

            }

        }

        Repeater {

            model: 6

            Item {

                height: 1; width: parent.width

                y: parent.height / 6 * index

                Rectangle { anchors.fill: parent; color: "#00FFFF" }

            }

        }

    }



    // --- COMPONENTE: INDICADOR DE DIRECCIONALES ---

    Row {

        anchors.top: parent.top

        anchors.topMargin: 20

        anchors.horizontalCenter: parent.horizontalCenter

        spacing: 400 // Separadas a los extremos del arco



        // Izquierda

        Item {

            width: 60; height: 40

            opacity: root.leftTurn ? 1.0 : 0.1

            Canvas {

                anchors.fill: parent

                onPaint: {

                    var ctx = getContext("2d");

                    ctx.fillStyle = "#00FF00";

                    ctx.beginPath();

                    ctx.moveTo(40, 0); ctx.lineTo(0, 20); ctx.lineTo(40, 40);

                    ctx.closePath(); ctx.fill();

                }

            }

        }

        // Derecha

        Item {

            width: 60; height: 40

            opacity: root.rightTurn ? 1.0 : 0.1

            Canvas {

                anchors.fill: parent

                layoutDirection: Qt.RightToLeft // Espejo

                onPaint: {

                    var ctx = getContext("2d");

                    ctx.fillStyle = "#00FF00";

                    ctx.beginPath();

                    ctx.moveTo(0, 0); ctx.lineTo(40, 20); ctx.lineTo(0, 40);

                    ctx.closePath(); ctx.fill();

                }

            }

        }

    }



    // --- COMPONENTE PRINCIPAL: TACÓMETRO (RPM) ---

    Item {

        id: tachometer

        width: 600; height: 600

        anchors.centerIn: parent

        anchors.verticalCenterOffset: 150 // Bajar el centro para que sea un arco superior



        Canvas {

            id: rpmCanvas

            anchors.fill: parent

            property real rpmPercentage: root.rpmVal / root.maxRPM



            onRpmPercentageChanged: requestPaint()



            onPaint: {

                var ctx = getContext("2d");

                var centerX = width / 2;

                var centerY = height / 2;

                var radius = 260;

                var startAngle = Math.PI * 0.8; // Inicio a la izquierda

                var endAngle = Math.PI * 2.2;   // Fin a la derecha

                var totalAngle = endAngle - startAngle;



                ctx.reset();



                // 1. Fondo del arco (Gris oscuro)

                ctx.beginPath();

                ctx.arc(centerX, centerY, radius, startAngle, endAngle, false);

                ctx.lineWidth = 25;

                ctx.strokeStyle = "#1a1a1a";

                ctx.stroke();



                // 2. Arco de RPM (Dinámico)

                var currentEndAngle = startAngle + (totalAngle * rpmPercentage);

                

                // Gradiente Lineal para el color

                var gradient = ctx.createLinearGradient(0, 0, width, 0);

                gradient.addColorStop(0.0, "#00FFFF"); // Cyan (Bajas)

                gradient.addColorStop(0.6, "#00FF00"); // Verde (Medias)

                gradient.addColorStop(0.85, "#FFFF00"); // Amarillo (Altas)

                gradient.addColorStop(1.0, "#FF0000"); // Rojo (Corte)



                ctx.beginPath();

                ctx.arc(centerX, centerY, radius, startAngle, currentEndAngle, false);

                ctx.lineWidth = 25;

                ctx.strokeStyle = gradient;

                ctx.lineCap = "butt"; // Bordes planos para look digital

                ctx.stroke();



                // 3. Marca de Redline (Visual)

                var redLineStart = startAngle + (totalAngle * (root.redLineRPM / root.maxRPM));

                ctx.beginPath();

                ctx.arc(centerX, centerY, radius + 20, redLineStart, endAngle, false);

                ctx.lineWidth = 4;

                ctx.strokeStyle = "#FF0000";

                ctx.stroke();

            }

        }

        

        // Texto RPM pequeño debajo

        Text {

            anchors.centerIn: parent

            anchors.verticalCenterOffset: -240

            text: Math.round(root.rpmVal)

            color: root.rpmVal > root.redLineRPM ? "red" : "#888"

            font.family: mainFont.name

            font.pixelSize: 24

        }

    }



    // --- PANEL CENTRAL: VELOCIDAD Y MARCHA ---

    ColumnLayout {

        anchors.centerIn: parent

        spacing: -10



        Text {

            text: Math.round(root.speedVal)

            color: "white"

            font.family: mainFont.name

            font.pixelSize: 160

            font.bold: true

            Layout.alignment: Qt.AlignHCenter

            style: Text.Outline

            styleColor: "#00FFFF" // Borde Cyan "Glow"

        }

        Text {

            text: "KM/H"

            color: "#00FFFF"

            font.family: mainFont.name

            font.pixelSize: 20

            font.letterSpacing: 10

            Layout.alignment: Qt.AlignHCenter

        }

        

        // Caja de Marcha (Gear)

        Rectangle {

            Layout.topMargin: 20

            Layout.alignment: Qt.AlignHCenter

            width: 80; height: 60

            color: "#222"

            border.color: gearVal === "N" ? "#00FF00" : "#555"

            border.width: 2

            radius: 5



            Text {

                anchors.centerIn: parent

                text: root.gearVal

                color: gearVal === "N" ? "#00FF00" : "white"

                font.family: mainFont.name

                font.pixelSize: 40

                font.bold: true

            }

        }

    }



    // --- PANELES INFERIORES (TEMP Y BATERÍA) ---

    RowLayout {

        anchors.bottom: parent.bottom

        anchors.bottomMargin: 30

        anchors.horizontalCenter: parent.horizontalCenter

        width: 700

        spacing: 300 // Separar a las esquinas



        // Izquierda: Temperatura

        Row {

            spacing: 15

            // Icono Termómetro (Dibujado con Shapes)

            Rectangle {

                width: 20; height: 50

                color: "transparent"

                border.color: root.tempVal > 100 ? "red" : "white"

                border.width: 2

                radius: 10

                

                // Líquido interno

                Rectangle {

                    width: 12; height: (root.tempVal / 120) * 40

                    color: root.tempVal > 100 ? "red" : (root.tempVal > 90 ? "yellow" : "#00FFFF")

                    radius: 4

                    anchors.bottom: parent.bottom

                    anchors.bottomMargin: 4

                    anchors.horizontalCenter: parent.horizontalCenter

                    

                    // Animación de parpadeo si es crítico

                    SequentialAnimation on opacity {

                        running: root.tempVal > 105

                        loops: Animation.Infinite

                        NumberAnimation { to: 0; duration: 200 }

                        NumberAnimation { to: 1; duration: 200 }

                    }

                }

            }

            

            Column {

                Text { 

                    text: Math.round(root.tempVal) + "°C"

                    color: "white"

                    font.family: mainFont.name

                    font.pixelSize: 28 

                }

                Text { 

                    text: "TEMP"

                    color: "#888"

                    font.family: mainFont.name

                    font.pixelSize: 12 

                }

            }

        }



        // Derecha: Batería

        Row {

            spacing: 15

            layoutDirection: Qt.RightToLeft // Texto a la izquierda del icono

            

            // Icono Batería

            Item {

                width: 50; height: 30

                Rectangle {

                    id: battBody

                    width: 44; height: 30

                    color: "transparent"

                    border.color: "white"

                    border.width: 2

                    radius: 3

                }

                Rectangle {

                    width: 4; height: 14

                    color: "white"

                    anchors.left: battBody.right

                    anchors.verticalCenter: battBody.verticalCenter

                }

                // Nivel de carga

                Rectangle {

                    width: (root.battVal / 15) * 40 // Escala aprox para 15V max

                    height: 22

                    x: 2; y: 4

                    color: root.battVal < 11.5 ? "red" : "#00FF00"

                }

            }

            

            Column {

                Text { 

                    text: root.battVal.toFixed(1) + "V"

                    color: "white"

                    font.family: mainFont.name

                    font.pixelSize: 28

                    anchors.right: parent.right 

                }

                Text { 

                    text: "BATT"

                    color: "#888"

                    font.family: mainFont.name

                    font.pixelSize: 12

                    anchors.right: parent.right 

                }

            }

        }

    }

}