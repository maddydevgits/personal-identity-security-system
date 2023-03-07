const file=artifacts.require('fileProtect');

module.exports=function(deployer) {
    deployer.deploy(file);
}