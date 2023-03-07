// SPDX-License-Identifier: MIT
pragma solidity >=0.4.22 <0.9.0;

contract register {
  
  // Contract Variables
  address[] _usernames; // dynamic array 
  string[] _names;
  uint[] _passwords;
  string[] _emails;
  string[] _mobiles;

  // avoid duplicate registrations
  mapping(address=>bool) _users;

  // INSERT INTO TABLE - inserting data
  // this function is used to insert data into the blockchain
  function registerUser(address username,string memory name, uint password,string memory email,string memory mobile) public {

    // whether user is already registered
    require(!_users[username]); // it throws error when user is already registered

    _usernames.push(username);
    _names.push(name);
    _passwords.push(password);
    _emails.push(email);
    _mobiles.push(mobile);
    _users[username]=true;
  }

  // function to return all this details
  // SELECT *
  function viewUsers() public view returns(address[] memory, string[] memory, uint[] memory, string[] memory, string[] memory){
    return(_usernames,_names,_passwords,_emails,_mobiles);
  }

  // function to check login
  function loginUser(address username,uint password) public view returns(bool){

    require(_users[username]);

    uint i;
    for(i=0;i<_usernames.length;i++){
      if(_usernames[i]==username && _passwords[i]==password){
        return true;
      }
    }
    return false;
  }
}
