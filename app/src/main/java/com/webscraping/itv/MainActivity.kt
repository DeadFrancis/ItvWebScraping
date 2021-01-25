package com.webscraping.itv

import android.annotation.SuppressLint
import android.os.Bundle
import android.text.method.ScrollingMovementMethod
import android.view.View
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.chaquo.python.PyObject
import com.chaquo.python.Python
import com.chaquo.python.android.AndroidPlatform
import java.util.*


class MainActivity : AppCompatActivity() {
    @SuppressLint("WrongViewCast", "SetTextI18n")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        //Declaración de los widgets
        val firstButton = findViewById<Button>(R.id.firstButton)
        val firstNumber = findViewById<EditText>(R.id.vehiclesNumber)
        val delayNumber = findViewById<EditText>(R.id.delayNumber)

        fun append(arr: Array<String>, element: String): Array<String> {
            val list: MutableList<String> = arr.toMutableList()
            list.add(element)
            return list.toTypedArray()
        }



        //Escucha del primer botón
        firstButton.setOnClickListener(View.OnClickListener {
            //Declaración de elementos + recogida de número de vehículos
            val inputText = firstNumber.text.toString()
            val inputNumber = inputText.toInt()
            val inputText2 = delayNumber.text.toString()
            val inputDelay = inputText2.toLong() * 60000  //Conversión a ms
            val matriculasArray: ArrayList<String> = arrayListOf<String>()
            val localizadoresArray: ArrayList<String> = arrayListOf<String>()
            var realNumber = 1
            var pressed = false
            var num = 0
            var hour = ""
            var minute = ""
            var second = ""
            var calendar = Calendar.getInstance()
            var obj: PyObject
            var actualText = ""



            //Cambio de layout + declaración de widgets
            setContentView(R.layout.second_layout)
            val matriculaLabel = findViewById<EditText>(R.id.matriculaText)
            val localizadorLabel = findViewById<EditText>(R.id.localizadorText)
            val secondButton = findViewById<Button>(R.id.secondButton)


            fun nextPage(){
                //Cambia el hint y el texto de los widgets del segundo layout
                matriculaLabel.setText("")
                localizadorLabel.setText("")
                matriculaLabel.hint = "Matrícula $realNumber"
                localizadorLabel.hint = "Localizador $realNumber"
                secondButton.text = "Vehículo $realNumber configurado"
            }

            fun arraysCollector(){
                matriculasArray.add(matriculaLabel.text.toString())
                localizadoresArray.add(localizadorLabel.text.toString())
            }

            nextPage()
            //Escucha del segundo botón
            secondButton.setOnClickListener( View.OnClickListener{
                if (realNumber < inputNumber) {
                    //Cambio de pantalla + recogida de datos
                    realNumber++
                    arraysCollector()
                    nextPage()
                }else if (realNumber == inputNumber){
                    //Recogida de datos
                    realNumber++
                    arraysCollector()
                    setContentView(R.layout.third_layout)
                    val mainLog = findViewById<TextView>(R.id.mainLog)
                    mainLog.movementMethod = ScrollingMovementMethod()
                    Thread{
                        if (!Python.isStarted()) {
                            Python.start(AndroidPlatform(this))
                        }
                        val py = Python.getInstance()
                        val pyobj = py.getModule("main")
                        while (!pressed) {
                            num ++
                            if (num != 1) {
                                actualText += "\n\n"
                            }
                            calendar = Calendar.getInstance()
                            hour = calendar.get(Calendar.HOUR_OF_DAY).toString()
                            minute = calendar.get(Calendar.MINUTE).toString()
                            second = calendar.get(Calendar.SECOND).toString()
                            actualText += "Conexión Número $num:  $hour:$minute:$second"
                            for (i in 0 until inputNumber){
                                obj = pyobj.callAttr("main", matriculasArray[i], localizadoresArray[i], 210)
                                actualText += "\n------------------------------\nPróxima cita ${matriculasArray[i]}:\n${obj.toString()}\n------------------------------"
                                mainLog.text = actualText
                            }
                            Thread.sleep(inputDelay)
                        }
                    }.start()
                }
            })
        })
    }
}