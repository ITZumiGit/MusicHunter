/**
 * useVisualizer — Audio Visualizer (Web Audio API + Canvas)
 * Рисует красивые частотные бары из аудио-сигнала
 */
import { ref, onUnmounted } from 'vue'

export function useVisualizer() {
  const isActive = ref(false)
  let audioContext: AudioContext | null = null
  let analyser: AnalyserNode | null = null
  let source: MediaElementAudioSourceNode | null = null
  let animationId: number | null = null
  let canvas: HTMLCanvasElement | null = null
  let ctx: CanvasRenderingContext2D | null = null
  let currentAudioElement: HTMLAudioElement | null = null
  const BAR_COUNT = 48
  const BAR_GAP = 2

  function init(audioElement: HTMLAudioElement, canvasElement: HTMLCanvasElement) {
    if (!audioElement || !canvasElement) return

    // Если уже инициализирован с этим же audio — просто переподключаем canvas
    if (currentAudioElement === audioElement && canvas) {
      canvas = canvasElement
      ctx = canvas.getContext('2d')
      startDrawing()
      return
    }

    cleanup()

    canvas = canvasElement
    ctx = canvas.getContext('2d')
    currentAudioElement = audioElement

    try {
      audioContext = new (window.AudioContext || (window as any).webkitAudioContext)()
      analyser = audioContext.createAnalyser()
      analyser.fftSize = 128
      analyser.smoothingTimeConstant = 0.8

      source = audioContext.createMediaElementSource(audioElement)
      source.connect(analyser)
      analyser.connect(audioContext.destination)

      isActive.value = true
      startDrawing()
    } catch (e) {
      console.warn('[Visualizer] Init failed:', e)
      isActive.value = false
    }
  }

  function startDrawing() {
    if (animationId) cancelAnimationFrame(animationId)
    draw()
  }

  function draw() {
    if (!canvas || !ctx || !analyser) return

    const bufferLength = analyser.frequencyBinCount
    const dataArray = new Uint8Array(bufferLength)

    const render = () => {
      animationId = requestAnimationFrame(render)
      analyser!.getByteFrequencyData(dataArray)

      const w = canvas!.width
      const h = canvas!.height
      ctx!.clearRect(0, 0, w, h)

      const barWidth = (w - BAR_GAP * (BAR_COUNT - 1)) / BAR_COUNT
      const step = Math.floor(bufferLength / BAR_COUNT)

      for (let i = 0; i < BAR_COUNT; i++) {
        const value = dataArray[i * step] || 0
        const barHeight = (value / 255) * h

        // Gradient color — from accent to pink
        const ratio = i / BAR_COUNT
        const r = Math.round(139 + (244 - 139) * ratio)
        const g = Math.round(92 + (114 - 92) * ratio)
        const b = Math.round(246 + (182 - 246) * ratio)

        ctx!.fillStyle = `rgba(${r}, ${g}, ${b}, 0.85)`

        const x = i * (barWidth + BAR_GAP)
        const y = h - barHeight

        // Rounded top bars
        const radius = Math.min(barWidth / 2, 3)
        ctx!.beginPath()
        ctx!.moveTo(x, h)
        ctx!.lineTo(x, y + radius)
        ctx!.quadraticCurveTo(x, y, x + radius, y)
        ctx!.lineTo(x + barWidth - radius, y)
        ctx!.quadraticCurveTo(x + barWidth, y, x + barWidth, y + radius)
        ctx!.lineTo(x + barWidth, h)
        ctx!.closePath()
        ctx!.fill()
      }
    }

    render()
  }

  function stop() {
    if (animationId) {
      cancelAnimationFrame(animationId)
      animationId = null
    }
    isActive.value = false
  }

  function cleanup() {
    stop()
    if (source) {
      try { source.disconnect() } catch {}
      source = null
    }
    if (analyser) {
      try { analyser.disconnect() } catch {}
      analyser = null
    }
    if (audioContext && audioContext.state !== 'closed') {
      audioContext.close().catch(() => {})
      audioContext = null
    }
    canvas = null
    ctx = null
  }

  onUnmounted(cleanup)

  return { init, stop, cleanup, isActive }
}
