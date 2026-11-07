@echo off
setlocal
cd /d "%~dp0"
if not exist ".audit_chunks" mkdir ".audit_chunks"
if /I "%~1"=="data" goto :data
:code
call :verify "01_code_logs_and_review.zip" "f631c13a7c3f28b66efafae543951e32e3d78c4ccf6f4594de9919e010685fba"
if not errorlevel 1 goto :code_done
if exist "01_code_logs_and_review.zip" goto :existing_error
call :fetch ".audit_chunks\code_001.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/code_001.bin" "d995384dfd75efb1aa12495a7bbe5022e741289239f0b42ad6db5b0133cd8ac5"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\code_002.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/code_002.bin" "8f9b8095f544cf98b2dd9ccc79e0bb3fd40bebf83070c8f01f069824262ae4bc"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\code_003.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/code_003.bin" "89b59d3c9c9dad64b38fc5e4979e88882bc87bdc83125894dfc29a0e8b124357"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\code_004.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/code_004.bin" "519406eef7e61071fdf488ad68bd63beb16f6ddc754b7afd3fde88ff5d170c95"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\code_005.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/code_005.bin" "d62fc0b1716f4c08e4e5c466cdfa293508e9b2af1158d206afe6b1288b37a1fc"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\code_006.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/code_006.bin" "f802f671da6132bd23d200a8f99b09f5578d91748fb50caf32ee7a27c91b7aff"
if errorlevel 1 goto :failed
copy /b /y ".audit_chunks\code_001.bin"+".audit_chunks\code_002.bin"+".audit_chunks\code_003.bin"+".audit_chunks\code_004.bin"+".audit_chunks\code_005.bin"+".audit_chunks\code_006.bin" "01_code_logs_and_review.zip.merging" >nul
if errorlevel 1 goto :failed
call :verify "01_code_logs_and_review.zip.merging" "f631c13a7c3f28b66efafae543951e32e3d78c4ccf6f4594de9919e010685fba"
if errorlevel 1 goto :failed
move /y "01_code_logs_and_review.zip.merging" "01_code_logs_and_review.zip" >nul
echo Merged and verified: 01_code_logs_and_review.zip
:code_done
if /I "%~1"=="code" goto :done
:data
call :verify "02_recent_data_models_and_weights.zip" "2c483103d04562569160c353c768a94389351b5b51b7637a9b480ec57a4f868f"
if not errorlevel 1 goto :data_done
if exist "02_recent_data_models_and_weights.zip" goto :existing_error
call :fetch ".audit_chunks\data_001.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_001.bin" "0ade247e7198dd4994a9379ea19bbcdffc6b993d27b0c0aba07bc0490ac0a6a2"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_002.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_002.bin" "034bfff6b4630c74dd95a25c2fd522188b082236baae39cd41e6002fae7b6569"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_003.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_003.bin" "bccb33f8292d8c85971829ef2b5a18e78c3c2b0d92400e47e0cbc5530c38fd23"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_004.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_004.bin" "97bf3a23808436e105484fdb93525f738649aeffaf59b8328378703089204601"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_005.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_005.bin" "d268083464f5c5d5eff74d1253522f4587da391d5005c14777ba5cf93ccb844c"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_006.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_006.bin" "ad60a327b168595ccef42912a0289be4c04460a2e7735f7fef94bb920e26d335"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_007.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_007.bin" "2568cc5d2b2423ec44aef782fc7083dc02a1b206a1ab5aeec99a6ff504d0fe09"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_008.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_008.bin" "a0ea0417838449761b9e8543933b001691ceeb104f694da8f2c8c096df2f329a"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_009.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_009.bin" "698cac9c0b27d977bb95816ec84687d016b473ca625f2d99d013efe0a857b2a6"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_010.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_010.bin" "1b24a98941f1af70183f2a947ede57b564fb3328f6a57775602e79fb84b7b4da"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_011.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_011.bin" "66fa9f90db8d1361242e436425fe99e235a4bdb5f57f7b70790742d6a18e17e3"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_012.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_012.bin" "7528dfa8af89fbb4d2c7c1d2c04e0667506eaa5e2588d5ee499782c6501d7f52"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_013.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_013.bin" "5919a807ac178b858a49306764f2dfb96ac42e534da4f3267425a8d0db42cb01"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_014.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_014.bin" "b29e24474475973f95a2ce0772a317b0f71d342d5b24024a2447e6de4b1282a9"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_015.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_015.bin" "92a6f6b944d31a0cdcfcdc1ecae081147b617bfa7c23cb443a5d6eca4e1137b7"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_016.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_016.bin" "438792352f50a93e88d8cd50c41c0bff603b9693c8c6b18e9afc79f1218e2bae"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_017.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_017.bin" "f92829e1da94e06377dfb9c5f197b6e13cc5c0e9873cc40378db6368ee2374b0"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_018.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_018.bin" "4adbfe95dc89b0de320769301309c34a1d26917f8b2cb1f9505437829af698c6"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_019.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_019.bin" "c3574be13593f2e98aa5a8a9dcc5c9f63c407ee04cae5c92c777624ae3266d28"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_020.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_020.bin" "60f432524b1d3cc241e0cbb9edb6ee39bb3ddd2627a4643db7656bc3388e93b8"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_021.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_021.bin" "338510a9f269f57cb757408b986a67f636f6f4785effeba67786c7beb6432159"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_022.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_022.bin" "06364c69b5c8ec7ae9c94a10d8da973bf97a50d28868bc36b63e4fcda91ec5d8"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_023.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_023.bin" "4be774badfb0858dd9614d43da03901f9cf89770bc3570411cb8ff09e8a0fcee"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_024.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_024.bin" "6a95fabc1a1d5affdb736bce5eb724dd3eefdf0cc23bc7ed5a5c9aab28ab034a"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_025.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_025.bin" "49b3583345e5c1fabe9d2ce43f828f5eb93a924ab688571098779f2f2c686a8d"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_026.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_026.bin" "2dca191a54266271f763285ba3b195bfa7aa60ed14aaa15a100c5e23592da732"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_027.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_027.bin" "d9ee603f6b71044849647cc4bba110a7a5fba59cc2dcc58f82cde5625a7e1b04"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_028.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_028.bin" "270531660f80991e43495de09fb7a04556c8b4d6c40e0de111ea72b719f4a211"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_029.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_029.bin" "cdba6f59fdfb30e68076eaba95ffae94ad7d36bdf5fe8b10058014318f5d7276"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_030.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_030.bin" "78fea0acb8ba0217a0d1bfa0a5eac23ec10c3c524225a4f620c1213f2cd0bb9c"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_031.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_031.bin" "4989e0ede63e398d856b9039562d6eae94606a125afaea060cf05000006f55b3"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_032.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_032.bin" "4edbd917e5d36092e517930b770c046147fbd6483d36472fc9f7584c228302c5"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_033.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_033.bin" "a7d37998c55e63615d6c3c67ab8bc0779cd05c6f7ce18e11d2d545fc04380be9"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_034.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_034.bin" "dd4958d97a1683c685cbe1e801d7b5c6d0efa15166d695097bd4a6d692070e15"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_035.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_035.bin" "8f75cf688212152fd12369069b7394a473b5c2700b07975bf63a401ac5b9345e"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_036.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_036.bin" "ee376714010f9c059b333019523c3bea5960a609104d708b5c000dfadf17eff0"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_037.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_037.bin" "54f79cb0eae49527cf9b2a700e324bbf1413fc86983be9debedd2e0b5e7f59a6"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_038.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_038.bin" "724776db31975f5e41408fdcc5753593e3cca6ad2c577097c7aa1fef0abe4dbd"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_039.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_039.bin" "f51c81a58db667d275b58e07db249a33f8f47d56dbd61d60822f557ee4c0f9e5"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_040.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_040.bin" "d3c1bbd40352fe47deffd08e9fd8f85707ab481ad9ee0de339bcc4aa78283d16"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_041.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_041.bin" "10ec2d2e2f3b01f7fcf910e7bcf274077aa7f0f572e834a790a8776f59ce29e5"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_042.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_042.bin" "915f3b416d1e1b44187a3f198f6354a8961dcd1077b401e38e9efdeb108c648d"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_043.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_043.bin" "13a0627e5bb7bcb16e58dc6d8245fd6311c91ddbc44d39dbb3533edf06e4dacb"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_044.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_044.bin" "9799bdb21c8555b8828c0e6295182421ab2e528ee714cef9c49830a9827936dc"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_045.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_045.bin" "2dbc136d6d4b496a36fde6ee47c61f0833dac8a570957b729a72b81c6d56056d"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_046.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_046.bin" "66c9aafad5a5b325376b03f9fc0576e3a5363f28547db67619abcfe204923d45"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_047.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_047.bin" "2acac9babc253acd7019ac832ae66e0d9d61610d92d8f1f6a129b5db3ffb6b34"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_048.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_048.bin" "ec258aa35d49f1cb58ddcc3050d0371f5a8be4b96c97ea408273d9263e95437b"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_049.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_049.bin" "21c5a0a85b09339990aa2f3fae86b9a2caf7c919791c5617acae2f8348d532be"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_050.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_050.bin" "653d2000dba2ba7e3bb9cc33813b3d99ba69b61ba9230da0f503871c68db5286"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_051.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_051.bin" "a34d9d2d40cec5b8bdfad4acfb466eeb0a2fecb48ee83ea924c3b56965b67e9e"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_052.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_052.bin" "f8479e50418f5e950ec879ac5904d0b65087f30a80221c3deadca5351830dd19"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_053.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_053.bin" "7998f833470e9aa9fad1b8d8c3d7d1ad891f5afc5d5a131f7d71ca572712fcad"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_054.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_054.bin" "0e925adefdf58baade191c9deaf4ccef399c211dd46bf19dc4c2c2d8b3bdb6e4"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_055.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_055.bin" "568e23145bc6cfcf5401a1f86e0bbf990d32f83bcec4fb112d715c9dfa29187f"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_056.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_056.bin" "0b3bc3b853c8f31d42d787f7ea9e7a233119d449b398cd4ac9a92ead8ceaa35d"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_057.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_057.bin" "b9e3cea09f165bcce4c141aaab188d4e22eba7fffbdc3031359d7544f35bded3"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_058.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_058.bin" "08ed11090b9fa517066c1fd72dc27251eb7f1245352434d860bd2448b1a1be90"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_059.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_059.bin" "87bf42a4375df90794c6ce5e62f9365a8399d199def9fc6df8e771a916e72593"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_060.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_060.bin" "e90947687ad4926e522b899b6f3562edf8364031121552a27fc8ff5dea5d754d"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_061.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_061.bin" "6ff228668ef5ebe107551b4bede270860c7ff9d040b0da964d1974b4f60e744e"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_062.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_062.bin" "015e7427676cfc3472953fe8d76f3e1ac64b69b6b64f8f57be6fa41a56304ab4"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_063.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_063.bin" "6926ced835836a969401b7492330641c7d3a833d2a68a339a9bc986c1296850d"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_064.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_064.bin" "92d9fb6339a442c85307eddc7220ee082693cc9f6de3d8f34584f185a5404d57"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_065.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_065.bin" "e7e97a5f02a0b05392f6526d12518b2cecce08848c91184191a0412194ccae88"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_066.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_066.bin" "c31b6fb59c47e31ed2dca50a7ea93cb31dd40ca1d27c745081c2a503cc172c2a"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_067.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_067.bin" "7b8fdd6fc18a872666ce2f719cbdbb8e1a8b7f3230f2016382b7abc3debe3a27"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_068.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_068.bin" "dd87c112120b66927f9b66debaccab2a194daa8c52661111a42f05b3b487b581"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_069.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_069.bin" "58d2e6d8f2dbee2ca9863f0bbd9dc2adfac71bb20a7cde7f77c8d0121d4dbd0e"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_070.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_070.bin" "66443b4c6485b6d06cec7049650cbe7365098827e49f00cfce289e46c07352bc"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_071.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_071.bin" "ecfb9061a88ce97604eff4275a972d08fa612e361bce40b8fbfbc272189b34d0"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_072.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_072.bin" "04353d4be8ff6436741b5691cf4644055bd1529a6246c9d93dce5716ccb34077"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_073.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_073.bin" "7b2b80811723fd33e5283676e194b1b1fab2e4e7de203dc1792f00e2e09c1271"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_074.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_074.bin" "5a41529cd194da9d31fcef2aa048942332752afcfa853cec92ac43061cd378e6"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_075.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_075.bin" "f31cb1da9f77dce2a05cf46c9763ccad7adecf80f4838abe782869ffc00b2f70"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_076.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_076.bin" "659a900dce6f2b97c012c0c07e15ced3886219a9d60db4981512260f9a322a12"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_077.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_077.bin" "f89773d952470ec5a51609c545925dbd948c4a6c209f76cbd35e687478bbc639"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_078.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_078.bin" "6ab05b83625606d5c5f16b3b5eda2e1af6ae288dab557290692088579ce954de"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_079.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_079.bin" "b33261d91ae782ff900264e1717cfeba2d2fc0d85a49d1ab0ec75e7437d18bc4"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_080.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_080.bin" "e57c3ba5b5bc0d2afc703bc2ce61abb024274543973ff87c0ef128935f638bbb"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_081.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_081.bin" "23d7ff66a81ddfb438b49d33e0642324ad5a9903d57524a6905c429219b9fe7c"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_082.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_082.bin" "b571b270f4a9cd287bae0aa1ee44f049ad6b0591641ccc1fb91356ef536f1a66"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_083.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_083.bin" "7f2a99e44a47a5ca752ca2d0924577fa21fde2477e28ddbe96234c9970a94226"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_084.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_084.bin" "405f6f2b9a69c593256c2a4e485e43cb7401b386b28f810cc9d17804399b5834"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_085.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_085.bin" "d1484b3bf814b48169c8bbd8ec771d8c42b2e442a3aed55c8612c6d6662de5ad"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_086.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_086.bin" "e89e92da2d682ac6e3bc5751ef6ed961ee582bb5e387067e42f5b5a0ad148efd"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_087.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_087.bin" "f5eb91ab34eada46ac4af58751a0470f31858678260ad0baec3d5d7d893891b4"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_088.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_088.bin" "4146224c9e10932dd9d432133460bd1259817be85fad4f5634b2b2e5cb3d2624"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_089.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_089.bin" "81389763cd562b097fe7a3c2b13ed2ea48292e9d90016476ba041857d89ae22b"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_090.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_090.bin" "21f2d09e9dd1222a429e38742167363c19d93e1a4a1586a793de6a3e241e536c"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_091.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_091.bin" "6f05a911fb4ecfbbd5182088877f1178675f34e550e145d08f81175778b2327b"
if errorlevel 1 goto :failed
call :fetch ".audit_chunks\data_092.bin" "https://raw.githubusercontent.com/linzhefeng24/Applepie/audit-downloads-20261107/audit_chunks/data_092.bin" "36bf3983c757cc60e1067b1749f1cc147f939ff97f9356eb4bf8ee1c70f0f12b"
if errorlevel 1 goto :failed
copy /b /y ".audit_chunks\data_001.bin"+".audit_chunks\data_002.bin"+".audit_chunks\data_003.bin"+".audit_chunks\data_004.bin"+".audit_chunks\data_005.bin"+".audit_chunks\data_006.bin"+".audit_chunks\data_007.bin"+".audit_chunks\data_008.bin"+".audit_chunks\data_009.bin"+".audit_chunks\data_010.bin"+".audit_chunks\data_011.bin"+".audit_chunks\data_012.bin"+".audit_chunks\data_013.bin"+".audit_chunks\data_014.bin"+".audit_chunks\data_015.bin"+".audit_chunks\data_016.bin"+".audit_chunks\data_017.bin"+".audit_chunks\data_018.bin"+".audit_chunks\data_019.bin"+".audit_chunks\data_020.bin"+".audit_chunks\data_021.bin"+".audit_chunks\data_022.bin"+".audit_chunks\data_023.bin"+".audit_chunks\data_024.bin"+".audit_chunks\data_025.bin"+".audit_chunks\data_026.bin"+".audit_chunks\data_027.bin"+".audit_chunks\data_028.bin"+".audit_chunks\data_029.bin"+".audit_chunks\data_030.bin"+".audit_chunks\data_031.bin"+".audit_chunks\data_032.bin"+".audit_chunks\data_033.bin"+".audit_chunks\data_034.bin"+".audit_chunks\data_035.bin"+".audit_chunks\data_036.bin"+".audit_chunks\data_037.bin"+".audit_chunks\data_038.bin"+".audit_chunks\data_039.bin"+".audit_chunks\data_040.bin"+".audit_chunks\data_041.bin"+".audit_chunks\data_042.bin"+".audit_chunks\data_043.bin"+".audit_chunks\data_044.bin"+".audit_chunks\data_045.bin"+".audit_chunks\data_046.bin"+".audit_chunks\data_047.bin"+".audit_chunks\data_048.bin"+".audit_chunks\data_049.bin"+".audit_chunks\data_050.bin"+".audit_chunks\data_051.bin"+".audit_chunks\data_052.bin"+".audit_chunks\data_053.bin"+".audit_chunks\data_054.bin"+".audit_chunks\data_055.bin"+".audit_chunks\data_056.bin"+".audit_chunks\data_057.bin"+".audit_chunks\data_058.bin"+".audit_chunks\data_059.bin"+".audit_chunks\data_060.bin"+".audit_chunks\data_061.bin"+".audit_chunks\data_062.bin"+".audit_chunks\data_063.bin"+".audit_chunks\data_064.bin"+".audit_chunks\data_065.bin"+".audit_chunks\data_066.bin"+".audit_chunks\data_067.bin"+".audit_chunks\data_068.bin"+".audit_chunks\data_069.bin"+".audit_chunks\data_070.bin"+".audit_chunks\data_071.bin"+".audit_chunks\data_072.bin"+".audit_chunks\data_073.bin"+".audit_chunks\data_074.bin"+".audit_chunks\data_075.bin"+".audit_chunks\data_076.bin"+".audit_chunks\data_077.bin"+".audit_chunks\data_078.bin"+".audit_chunks\data_079.bin"+".audit_chunks\data_080.bin"+".audit_chunks\data_081.bin"+".audit_chunks\data_082.bin"+".audit_chunks\data_083.bin"+".audit_chunks\data_084.bin"+".audit_chunks\data_085.bin"+".audit_chunks\data_086.bin"+".audit_chunks\data_087.bin"+".audit_chunks\data_088.bin"+".audit_chunks\data_089.bin"+".audit_chunks\data_090.bin"+".audit_chunks\data_091.bin"+".audit_chunks\data_092.bin" "02_recent_data_models_and_weights.zip.merging" >nul
if errorlevel 1 goto :failed
call :verify "02_recent_data_models_and_weights.zip.merging" "2c483103d04562569160c353c768a94389351b5b51b7637a9b480ec57a4f868f"
if errorlevel 1 goto :failed
move /y "02_recent_data_models_and_weights.zip.merging" "02_recent_data_models_and_weights.zip" >nul
echo Merged and verified: 02_recent_data_models_and_weights.zip
:data_done
goto :done
:fetch
call :verify "%~1" "%~3" >nul 2>&1
if not errorlevel 1 exit /b 0
echo Downloading %~1
curl.exe --fail --location --retry 3 --continue-at - --output "%~1" "%~2"
if errorlevel 1 exit /b 1
call :verify "%~1" "%~3"
exit /b %errorlevel%
:verify
powershell -NoProfile -Command "if (!(Test-Path -LiteralPath '%~1')) {exit 1}; if ((Get-FileHash -LiteralPath '%~1' -Algorithm SHA256).Hash -ne '%~2') {exit 1}"
exit /b %errorlevel%
:existing_error
echo An existing ZIP has a different checksum. Rename it and run this file again.
goto :failed
:failed
echo Download or verification failed. The partial files are kept for retry.
pause
exit /b 1
:done
echo All requested files are verified. You can now extract the ZIP files.
pause
exit /b 0
