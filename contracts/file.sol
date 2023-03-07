// SPDX-License-Identifier: MIT
pragma solidity >=0.4.22 <0.9.0;

contract fileProtect {
  address[] _users;
  string[] _files;
  string[] _names;
  address[][] _tokens;

  mapping(string=>bool) files;

  function addFile(address user,string memory name,string memory fileT) public {
    require(!files[fileT]);

    files[fileT]=true;
    _users.push(user);
    _names.push(name);
    _files.push(fileT);
    _tokens.push([user]);
  }

  function viewFiles() public view returns(address[] memory,string[] memory,string[] memory,address[][] memory){
    return(_users,_names,_files,_tokens);
  }

  function addToken(string memory file,address user) public {
    uint i;
    
    for(i=0;i<_files.length;i++){
        if(keccak256(abi.encodePacked(file)) == keccak256(abi.encodePacked(_files[i]))){
            _tokens[i].push(user);
        }
    }
  }

  function removeToken(string memory file,address user) public {
    uint i;
    uint j;

    for(i=0;i<_files.length;i++){
        if(keccak256(abi.encodePacked(file)) == keccak256(abi.encodePacked(_files[i]))){
            for(j=0;j<_tokens[i].length;j++){
                if(_tokens[i][j]==user){
                    delete _tokens[i][j];
                }
            }
        }
    }
  }
}
