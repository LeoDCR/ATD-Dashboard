import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Shapes 1.15

Window {
    id: root
    visible: true
    width: 1024
    height: 1000
    title: "Moto Dashboard"
    color: "#050505"

    // --- PROPIEDADES ---
    property real speedVal: 0
    property real rpmVal: 0 // Ya no se usa para el aro, pero la dejamos por si Python la manda
    property real tempVal: 85
    property real fuelVal: 100 
    property string gearVal: "N"
    property bool leftTurn: false
    property bool rightTurn: false
    property bool lowBeam: false
    property bool highBeam: false

    // --- NUEVOS LÍMITES DE VELOCIDAD PARA EL ARO ---
    readonly property real maxSpeedArc: 320
    readonly property real redLineSpeed: 280 // La rayita roja exterior empieza a los 280 km/h

    FontLoader {
        id: mainFont
        source: "Orbitron-VariableFont_wght.ttf"
    }

    // =========================================================
    //   CONEXIÓN CON PYTHON (EL NUEVO CEREBRO)
    // =========================================================
    Connections {
        target: backend
        
        function onSpeedChanged(val) { root.speedVal = val }
        function onRpmChanged(val) { root.rpmVal = val }
        function onTempChanged(val) { root.tempVal = val }
        function onFuelChanged(val) { root.fuelVal = val }
        
        function onLightsChanged(low, high) { 
            root.lowBeam = low; 
            root.highBeam = high; 
        }
        
        function onTurnSignalsChanged(left, right) { 
            root.leftTurn = left; 
            root.rightTurn = right; 
        }
    }

    // =========================================================
    //    ELEMENTOS DE ESQUINA SUPERIOR (DIRECCIONALES)
    // =========================================================

    // DIRECCIONAL IZQUIERDA
    Item {
        width: 80; height: 60
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.margins: 30
        opacity: root.leftTurn ? 1.0 : 0.15
        Canvas {
            anchors.fill: parent
            onPaint: {
                var ctx = getContext("2d");
                ctx.fillStyle = "#00FF00";
                ctx.beginPath();
                ctx.moveTo(60, 10); ctx.lineTo(10, 30); ctx.lineTo(60, 50);
                ctx.closePath(); ctx.fill();
            }
        }
    }

    // DIRECCIONAL DERECHA
    Item {
        width: 80; height: 60
        anchors.top: parent.top
        anchors.right: parent.right
        anchors.margins: 30
        opacity: root.rightTurn ? 1.0 : 0.15
        Canvas {
            anchors.fill: parent
            onPaint: {
                var ctx = getContext("2d");
                ctx.fillStyle = "#00FF00";
                ctx.beginPath();
                ctx.moveTo(20, 10); ctx.lineTo(70, 30); ctx.lineTo(20, 50);
                ctx.closePath(); ctx.fill();
            }
        }
    }

    // =========================================================
    //    CLUSTER CENTRAL (ARCO DE VELOCIDAD, NÚMERO, LUCES)
    // =========================================================

    // 1. EL ARCO DE VELOCIDAD (Antes Tacómetro)
    Item {
        id: tachometer
        width: 600; height: 600
        anchors.centerIn: parent 
        
        Canvas {
            id: speedArcCanvas
            anchors.fill: parent
            
            // Calculamos el porcentaje basado en la velocidad actual y el límite de 320
            // Math.min asegura que nunca pase de 1.0 (100%) aunque vayas a 350km/h
            property real arcPercentage: Math.min(root.speedVal / root.maxSpeedArc, 1.0)
            
            // Cada que cambia el porcentaje de velocidad, se redibuja el aro
            onArcPercentageChanged: requestPaint()

            onPaint: {
                var ctx = getContext("2d");
                var centerX = width / 2;
                var centerY = height / 2;
                var radius = 260;
                var startAngle = Math.PI * 0.75; 
                var endAngle = Math.PI * 2.25; 
                var totalAngle = endAngle - startAngle;

                ctx.reset();
                ctx.lineCap = "round"; 

                // Fondo Gris del aro
                ctx.beginPath();
                ctx.arc(centerX, centerY, radius, startAngle, endAngle, false);
                ctx.lineWidth = 25; ctx.strokeStyle = "#1a1a1a"; ctx.stroke();

                // Arco de Velocidad dinámico
                var currentEndAngle = startAngle + (totalAngle * arcPercentage);
                var gradient = ctx.createLinearGradient(0, 0, width, 0);
                gradient.addColorStop(0.0, "#00FFFF"); gradient.addColorStop(0.5, "#00FF00"); gradient.addColorStop(1.0, "#FF0000");

                ctx.beginPath();
                ctx.arc(centerX, centerY, radius, startAngle, currentEndAngle, false);
                ctx.lineWidth = 25; ctx.strokeStyle = gradient; ctx.stroke();

                // Redline (Empieza en 280 km/h)
                var redLineStart = startAngle + (totalAngle * (root.redLineSpeed / root.maxSpeedArc));
                ctx.beginPath();
                ctx.arc(centerX, centerY, radius + 25, redLineStart, endAngle, false);
                ctx.lineWidth = 4; ctx.strokeStyle = "#FF0000"; ctx.stroke();
            }
        }
    }

    // 2. INFORMACIÓN CENTRAL (LUCES + VELOCIDAD)
    ColumnLayout {
        anchors.centerIn: parent
        spacing: -15 

        // A. LUCES (Baja/Alta)
        Canvas {
            id: lightsDisplay
            Layout.alignment: Qt.AlignHCenter
            width: 240; height: 80 
            Layout.bottomMargin: 10

            property bool lowOn: root.lowBeam
            property bool highOn: root.highBeam
            onLowOnChanged: requestPaint()
            onHighOnChanged: requestPaint()

            onPaint: {
                var ctx = getContext("2d");
                ctx.reset();
                ctx.lineCap = "round"; ctx.lineJoin = "round";

                // LUZ BAJA (Verde)
                if (root.lowBeam) {
                    ctx.strokeStyle = "#00FF00"; ctx.lineWidth = 6; 
                    
                    // Icono "D"
                    ctx.beginPath(); ctx.arc(70, 40, 18, -Math.PI/2, Math.PI/2, false); ctx.closePath(); ctx.stroke();
                    
                    // 4 RAYOS
                    ctx.beginPath(); 
                    ctx.moveTo(50, 25); ctx.lineTo(30, 35); 
                    ctx.moveTo(50, 34); ctx.lineTo(30, 44); 
                    ctx.moveTo(50, 43); ctx.lineTo(30, 53); 
                    ctx.moveTo(50, 52); ctx.lineTo(30, 62); 
                    ctx.stroke();
                }

                // LUZ ALTA (Azul)
                if (root.highBeam) {
                    ctx.strokeStyle = "#00AEFF"; ctx.lineWidth = 6; 
                    
                    // Icono "D"
                    ctx.beginPath(); ctx.arc(170, 40, 18, -Math.PI/2, Math.PI/2, false); ctx.closePath(); ctx.stroke();
                    
                    // 4 RAYOS
                    ctx.beginPath(); 
                    ctx.moveTo(150, 25); ctx.lineTo(125, 25); 
                    ctx.moveTo(150, 35); ctx.lineTo(125, 35); 
                    ctx.moveTo(150, 45); ctx.lineTo(125, 45); 
                    ctx.moveTo(150, 55); ctx.lineTo(125, 55); 
                    ctx.stroke();
                }
            }
        }

        // B. NÚMERO VELOCIDAD
        Text {
            text: Math.round(root.speedVal)
            color: "white"
            font.family: mainFont.name
            font.pixelSize: 180
            font.bold: true
            Layout.alignment: Qt.AlignHCenter
            style: Text.Outline; styleColor: "#00FFFF"
        }

        // C. ETIQUETA KM/H
        Text {
            text: "KM/H"
            color: "#00FFFF"
            font.family: mainFont.name
            font.pixelSize: 20
            font.letterSpacing: 10
            Layout.alignment: Qt.AlignHCenter
        }
    }

    // =========================================================
    //    ELEMENTOS DE ESQUINA INFERIOR (TEMP Y GASOLINA)
    // =========================================================

    // 1. TEMPERATURA
    Row {
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 40 
        anchors.left: parent.left
        anchors.leftMargin: 80 
        spacing: 15

        Rectangle { 
            width: 20; height: 50; color: "transparent"; border.color: root.tempVal > 100 ? "red" : "white"; border.width: 2; radius: 10
            Rectangle { 
                width: 12; height: (root.tempVal / 120) * 40; color: root.tempVal > 100 ? "red" : (root.tempVal > 90 ? "yellow" : "#00FFFF"); radius: 4; 
                anchors.bottom: parent.bottom; anchors.bottomMargin: 4; anchors.horizontalCenter: parent.horizontalCenter 
            } 
        }
        Column { 
            Text { text: Math.round(root.tempVal) + "°C"; color: "white"; font.family: mainFont.name; font.pixelSize: 28 } 
            Text { text: "TEMP"; color: "#888"; font.family: mainFont.name; font.pixelSize: 12 } 
        }
    }

    // 2. GASOLINA
    Row {
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 40
        anchors.right: parent.right
        anchors.rightMargin: 80 
        spacing: 20
        
        // Letra F y Cuña
        Item {
            width: 20; height: 80
            anchors.verticalCenter: parent.verticalCenter
            Canvas {
                anchors.fill: parent
                onPaint: {
                    var ctx = getContext("2d");
                    ctx.strokeStyle = "#00AEFF"; ctx.fillStyle = "#00AEFF"; ctx.lineWidth = 2;
                    ctx.font = "bold 16px sans-serif"; ctx.fillText("F", 0, 15);
                    ctx.beginPath(); ctx.moveTo(5, 20); ctx.lineTo(15, 20); ctx.lineTo(10, 80); ctx.closePath(); ctx.stroke();
                }
            }
        }

        // Barras
        Column {
            spacing: 4
            anchors.verticalCenter: parent.verticalCenter
            Repeater {
                model: 10
                Rectangle {
                    width: 35; height: 6; radius: 1
                    color: {
                        if (index >= 8) return "#FF0000"
                        if (index >= 5) return "#FFFF00"
                        return "#00FF00"
                    }
                    property int barThreshold: (9 - index) * 10
                    opacity: root.fuelVal > barThreshold ? 1.0 : 0.2
                    layer.enabled: root.fuelVal > barThreshold
                    border.width: root.fuelVal > barThreshold ? 0 : 1; border.color: "#333"
                }
            }
        }

        // Icono Bomba
        Item {
            width: 40; height: 40
            anchors.verticalCenter: parent.verticalCenter
            Canvas {
                anchors.fill: parent
                onPaint: {
                    var ctx = getContext("2d");
                    ctx.strokeStyle = "#00AEFF"; ctx.lineWidth = 2; ctx.lineJoin = "round";
                    ctx.strokeRect(5, 10, 20, 25);
                    ctx.beginPath(); ctx.moveTo(2, 35); ctx.lineTo(28, 35); ctx.stroke();
                    ctx.strokeRect(10, 15, 10, 8);
                    ctx.beginPath(); ctx.moveTo(25, 15); ctx.bezierCurveTo(35, 15, 35, 30, 25, 25); ctx.lineTo(25, 20); ctx.stroke();
                }
            }
        }
    }
}