<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  const dispatch = createEventDispatcher();

  function handleClose() {
    dispatch('close');
  }
</script>

<div class="fixed inset-0 bg-black/20 flex items-center justify-center z-50">
  <div class="bg-white rounded-lg p-6 w-98 shadow-lg">
    <h2 class="text-lg font-bold mb-4">도움말❓</h2>
    <div class="mb-4 space-y-2 text-sm text-gray-800 leading-relaxed">
    <ul class="list-disc list-inside">
        <li>메시지를 입력 후 전송 버튼을 누르면 AI가 응답합니다.</li>
        <li>송금 시에, 승인 여부를 확인하는 팝업이 나타납니다.</li>
        <li>송금은 '본인 음성 인증' 후에 팝업창에서 진행할 수 있습니다.</li>
        <li>한정 금액 이상을 보낼 시에 경고창이 출력됩니다.</li>
        <li>마이크 버튼을 누르면 5초간 녹음 후 자동 텍스트 변환됩니다.</li>
    </ul>
    </div>
    <button
      on:click={handleClose}
      class="px-4 py-2 bg-gray-200 rounded hover:bg-gray-300"
    >
      확인
    </button>
  </div>
</div>
