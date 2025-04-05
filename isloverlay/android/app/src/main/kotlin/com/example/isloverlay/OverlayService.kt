    package com.example.isloverlay

    import android.app.Notification
    import android.app.NotificationChannel
    import android.app.NotificationManager
    import android.content.Intent
    import android.graphics.PixelFormat
    import android.graphics.drawable.GradientDrawable
    import android.os.Build
    import android.os.IBinder
    import android.util.Log
    import android.view.*
    import android.widget.Button
    import android.widget.FrameLayout
    import androidx.camera.core.CameraSelector
    import androidx.camera.core.Preview
    import androidx.camera.lifecycle.ProcessCameraProvider
    import androidx.camera.view.PreviewView
    import androidx.core.content.ContextCompat
    import androidx.lifecycle.LifecycleOwner
    import androidx.lifecycle.LifecycleService
    import androidx.camera.core.ImageAnalysis
    import androidx.camera.core.ImageProxy
    import okhttp3.*
    import okio.ByteString
    import java.io.ByteArrayOutputStream
    import java.nio.ByteBuffer
    import android.graphics.YuvImage
    import android.graphics.ImageFormat
    import android.graphics.Rect

    class OverlayService : LifecycleService() {

        private lateinit var windowManager: WindowManager
        private lateinit var overlayView: View
        private lateinit var previewView: PreviewView
        private lateinit var switchCameraButton: Button
        private var isUsingBackCamera = true
        private var webSocket: WebSocket? = null
        private val client = OkHttpClient()

        override fun onCreate() {
            super.onCreate()

            // Foreground service notification
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                val channelId = "isl_overlay_channel"
                val channelName = "ISL Overlay Service"
                val chan = NotificationChannel(
                    channelId, channelName, NotificationManager.IMPORTANCE_MIN
                )
                val manager = getSystemService(NotificationManager::class.java)
                manager.createNotificationChannel(chan)

                val notification = Notification.Builder(this, channelId)
                    .setContentTitle("ISL Overlay Running")
                    .setContentText("You can now switch to WhatsApp and perform signs.")
                    .setSmallIcon(android.R.drawable.ic_menu_camera)
                    .setOngoing(true)
                    .build()

                startForeground(1, notification)
            }

            windowManager = getSystemService(WINDOW_SERVICE) as WindowManager

            val layoutParams = WindowManager.LayoutParams(
                480, // Width
                640, // Height
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O)
                    WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY
                else
                    WindowManager.LayoutParams.TYPE_PHONE,
                WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE or
                        WindowManager.LayoutParams.FLAG_LAYOUT_IN_SCREEN,
                PixelFormat.TRANSLUCENT
            )

            layoutParams.gravity = Gravity.TOP or Gravity.START
            layoutParams.x = 100
            layoutParams.y = 100

            // Overlay with rounded corners
            val background = GradientDrawable()
            background.cornerRadius = 50f
            background.setColor(0xAA000000.toInt()) // semi-transparent black

            val container = FrameLayout(this)
            container.background = background

            previewView = PreviewView(this)
            previewView.layoutParams = FrameLayout.LayoutParams(
                FrameLayout.LayoutParams.MATCH_PARENT,
                FrameLayout.LayoutParams.MATCH_PARENT
            )

            // Switch camera button
            switchCameraButton = Button(this).apply {
                text = "Switch"
                alpha = 0.8f
                textSize = 10f
                setOnClickListener {
                    isUsingBackCamera = !isUsingBackCamera
                    startCamera()
                }
            }
            val buttonParams = FrameLayout.LayoutParams(
                FrameLayout.LayoutParams.WRAP_CONTENT,
                FrameLayout.LayoutParams.WRAP_CONTENT,
                Gravity.BOTTOM or Gravity.END
            )
            buttonParams.setMargins(0, 0, 20, 20)

            // Close ("X") button
            val closeButton = Button(this).apply {
                text = "X"
                alpha = 0.8f
                textSize = 12f
                setOnClickListener {
                    stopSelf()
                }
            }
            val closeParams = FrameLayout.LayoutParams(
                FrameLayout.LayoutParams.WRAP_CONTENT,
                FrameLayout.LayoutParams.WRAP_CONTENT,
                Gravity.TOP or Gravity.END
            )
            closeParams.setMargins(0, 20, 20, 0)

            container.addView(previewView)
            container.addView(closeButton, closeParams)
            container.addView(switchCameraButton, buttonParams)

            overlayView = container
            windowManager.addView(overlayView, layoutParams)

            val request = Request.Builder().url("ws://192.168.244.170:8000/ws").build()
            webSocket = client.newWebSocket(request, object : WebSocketListener() {
                override fun onOpen(webSocket: WebSocket, response: Response) {
                    Log.d("WebSocket", "Connected to backend")
                }

                override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
                    Log.e("WebSocket", "WebSocket Error: ${t.message}")
                }

                override fun onClosed(webSocket: WebSocket, code: Int, reason: String) {
                    Log.d("WebSocket", "WebSocket Closed: $code - $reason")
                }
            })

            startCamera()
            makeDraggable(overlayView, layoutParams)
        }

        private fun makeDraggable(view: View, layoutParams: WindowManager.LayoutParams) {
            view.setOnTouchListener(object : View.OnTouchListener {
                private var initialX = 0
                private var initialY = 0
                private var initialTouchX = 0f
                private var initialTouchY = 0f

                override fun onTouch(v: View, event: MotionEvent): Boolean {
                    when (event.action) {
                        MotionEvent.ACTION_DOWN -> {
                            initialX = layoutParams.x
                            initialY = layoutParams.y
                            initialTouchX = event.rawX
                            initialTouchY = event.rawY
                            return true
                        }

                        MotionEvent.ACTION_MOVE -> {
                            layoutParams.x = initialX + (event.rawX - initialTouchX).toInt()
                            layoutParams.y = initialY + (event.rawY - initialTouchY).toInt()
                            windowManager.updateViewLayout(view, layoutParams)
                            return true
                        }
                    }
                    return false
                }
            })
        }

        private fun startCamera() {
            val cameraProviderFuture = ProcessCameraProvider.getInstance(this)
            cameraProviderFuture.addListener({
                val cameraProvider = cameraProviderFuture.get()

                val preview = Preview.Builder().build().also {
                    it.setSurfaceProvider(previewView.surfaceProvider)
                }

                val cameraSelector = if (isUsingBackCamera)
                    CameraSelector.DEFAULT_BACK_CAMERA
                else
                    CameraSelector.DEFAULT_FRONT_CAMERA

                val imageAnalyzer = ImageAnalysis.Builder()
                    .setBackpressureStrategy(ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST)
                    .build()

                imageAnalyzer.setAnalyzer(ContextCompat.getMainExecutor(this)) { imageProxy ->
                    processImageProxy(imageProxy)
                }

                try {
                    cameraProvider.unbindAll()
                    cameraProvider.bindToLifecycle(
                        this as LifecycleOwner,
                        cameraSelector,
                        preview,
                        imageAnalyzer
                    )
                } catch (e: Exception) {
                    Log.e("CameraX", "Failed to bind camera use cases", e)
                }
            }, ContextCompat.getMainExecutor(this))
        }

        private fun processImageProxy(image: ImageProxy) {
            val jpegBytes = imageProxyToJpeg(image)
            if (jpegBytes != null) {
                webSocket?.send(ByteString.of(*jpegBytes)) // ✅ Send as proper JPEG
            }
            image.close()
        }


        private fun imageProxyToJpeg(image: ImageProxy): ByteArray? {
            val yuvBytes = yuv420ToNv21(image) ?: return null
            val yuvImage = YuvImage(yuvBytes, ImageFormat.NV21, image.width, image.height, null)
            val out = ByteArrayOutputStream()
            yuvImage.compressToJpeg(Rect(0, 0, image.width, image.height), 60, out)
            return out.toByteArray()
        }

        private fun yuv420ToNv21(image: ImageProxy): ByteArray? {
            val yPlane = image.planes[0]
            val uPlane = image.planes[1]
            val vPlane = image.planes[2]

            val yBuffer = yPlane.buffer
            val uBuffer = uPlane.buffer
            val vBuffer = vPlane.buffer

            val ySize = yBuffer.remaining()
            val uSize = uBuffer.remaining()
            val vSize = vBuffer.remaining()

            val nv21 = ByteArray(ySize + uSize + vSize)

            yBuffer.get(nv21, 0, ySize)

            val chromaRowStride = uPlane.rowStride
            val chromaPixelStride = uPlane.pixelStride

            val width = image.width
            val height = image.height
            val chromaHeight = height / 2
            val chromaWidth = width / 2

            var outputOffset = ySize

            val uBufferPos = uBuffer.position()
            val vBufferPos = vBuffer.position()

            for (row in 0 until chromaHeight) {
                for (col in 0 until chromaWidth) {
                    val uIndex = uBufferPos + row * chromaRowStride + col * chromaPixelStride
                    val vIndex = vBufferPos + row * chromaRowStride + col * chromaPixelStride

                    nv21[outputOffset++] = vBuffer.get(vIndex)  // V first
                    nv21[outputOffset++] = uBuffer.get(uIndex)  // then U
                }
            }

            return nv21
        }




        override fun onDestroy() {
            super.onDestroy()
            if (::overlayView.isInitialized) {
                windowManager.removeView(overlayView)
            }
        }

        override fun onBind(intent: Intent): IBinder? {
            return super.onBind(intent)
        }
    }
