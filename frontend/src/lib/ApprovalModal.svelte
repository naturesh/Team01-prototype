<script lang="ts">
  import { ApprovalModalStore } from './store';
  import { onMount } from 'svelte';

  export let name: string;
  export let parameters: { [key: string]: any };

  let localData: { [key: string]: any } = {};
  let voice: string | null | any = null

  onMount(() => {
    localData = { ...parameters };
  });

  function handleSubmit() {

    if (voice == null) {
      alert('please record voice')
      return
    }

    // 원본 data의 타입에 맞게 변환
    const result: { [key: string]: any } = {};
    for (const key in localData) {
      const original = parameters[key];
      const value = localData[key];
      switch (typeof original) {
        case 'number':
          result[key] = Number(value);
          break;
        case 'boolean':
          result[key] = !!value;
          break;
        default:
          result[key] = value;
      }
    }
    result.voice = voice
    $ApprovalModalStore?.resolver?.(result);
    ApprovalModalStore.set(null);
  }

  function handleCancel() {
    $ApprovalModalStore?.resolver?.(null);
    ApprovalModalStore.set(null);
  }


  import RecordRTC from 'recordrtc';
  async function record() {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    
    // 1. WAV 형식 강제 설정
    const recorder = new RecordRTC(stream, {
        type: 'audio',
        mimeType: 'audio/wav',
        recorderType: RecordRTC.StereoAudioRecorder, // 핵심 변경점 (WAV 강제 지정)
        desiredSampRate: 16000,
        numberOfAudioChannels: 1 // 1채널(모노)로 설정 (필요시 조정)
    });

    recorder.startRecording();
    console.log('Recording started');

    return new Promise((resolve, reject) => {
        setTimeout(() => {
            recorder.stopRecording(async () => {
                try {
                    // 2. getBlob() 대신 getDataURL() 직접 사용
                    const dataURL = recorder.getDataURL((dataURL) => {
                        const base64 = dataURL.split(',')[1];
                        
                        // 3. 스트림 정리
                        stream.getTracks().forEach(track => track.stop());
                        recorder.destroy();
                        
                        resolve(base64);
                    });
                } catch (e) {
                    stream.getTracks().forEach(track => track.stop());
                    recorder.destroy();
                    reject(e);
                }
            });
        }, 5000);
    });
}





</script>





<div class="fixed inset-0 bg-black/10 flex items-center justify-center z-50">
  <div class="bg-[#f4ede1] p-8 min-w-[320px] max-w-[90vw] shadow-lg rounded-3xl">
    <h2 class="text-xl font-bold mb-6">{name}</h2>
    <button class="border rounded-3xl p-4" on:click={() => record().then(base64 => voice = base64)}>record voice</button>
    <form on:submit|preventDefault={handleSubmit}>
      {#each Object.entries(localData) as [key, value]}
        <div class="mb-4">
          <span class="block mb-2 font-medium">{key}</span>
          {#if typeof parameters[key] === 'boolean'}
            <input
              type="checkbox"
              class="h-5 w-5"
              bind:checked={localData[key]}
            />
          {:else if typeof parameters[key] === 'number'}
            <input
              type="number"
              class="w-full px-3 py-2 border rounded focus:outline-none focus:ring"
              bind:value={localData[key]}
            />
          {:else}
            <input
              type="text"
              class="w-full px-3 py-2 border rounded focus:outline-none focus:ring"
              bind:value={localData[key]}
            />
          {/if}
        </div>
      {/each}
      <div class="flex gap-3 justify-end mt-6">
        <button type="button" class="px-4 py-2 rounded border bg-gray-100 hover:bg-gray-200" on:click={handleCancel}>취소</button>
        <button type="submit" class="px-4 py-2 rounded bg-lime-600 text-white hover:bg-lime-700">확인</button>
      </div>
    </form>
  </div>
</div>
