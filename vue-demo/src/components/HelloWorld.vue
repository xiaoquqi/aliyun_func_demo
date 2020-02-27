<template>
  <div class="demo-image">
    <div class="block-container" v-for="p in persons" :key="p.id">
      <p class="demonstration">{{p.id}}. {{ p.uuid }}</p>
      <div class="block" v-for="f in p.faces" :key="f.id">
        <el-image
          style="width: 200px"
          :src="f.url"></el-image>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'HelloWorld',
  data () {
    return {
      persons: []
    }
  },
  mounted () {
    axios.get('http://11820831.1897056164648918.functioncompute.com/persons')
      .then(response => { this.persons = response.data })
  }
}
</script>

<!-- Add 'scoped' attribute to limit CSS to this component only -->
<style scoped>
  .block-container{
    margin-left: 20px;
  }
  .block-container p{
    padding: 10px 0;
    background: #f2f2f2;
    text-indent: 20px;
  }
  .block-container .block{
    display: inline-block;
    margin-left: 40px;
  }
  .block-container .block img{
    width: 200px;
  }
</style>
