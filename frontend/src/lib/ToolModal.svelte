<script lang="ts">
  import { ToolModalStore } from './store';

  import checkImage from '../assets/tool_success.png'
  export let name: string;
  export let title: string | undefined;
  
  function handleSubmit() {

    $ToolModalStore?.resolver?.(null);
    ToolModalStore.set(null);
  }

  setTimeout(() => {
    handleSubmit()
  }, 1500);

</script>

<div class="fixed inset-0 bg-black/10 flex items-center justify-center z-50">
  <div class="bg-[#f4ede1] rounded-3xl p-8 w-96 shadow-lg aspect-square">
    <h2 class="text-xl font-extrabold mb-6 text-center w-full">{title || '도구를 사용했어요!'}<br> <span class="font-light text-sm">- {name.toLowerCase()} -</span></h2>
    
    <div class="flex justify-center items-center w-full h-3/4">
      <img src={checkImage} width="50%" height="50%" alt="">
    </div>
   
  </div>
</div>
