package main

import (
    "fmt"

    "strings"
    "encoding/json"
    "github.com/hyperledger/fabric/core/chaincode/shim"
    "github.com/hyperledger/fabric/protos/peer"
)

type SimpleAsset struct {
}

type State [][]string

// An important structure which describes a valid format for the update function argument.
type UpdateAsset struct{
	Prestate State `json:"prestate"`
	Commands State `json:"commands"`
}

// A stub for the init method which always returns Success since we dont need any specific action to initialize the ledger
func (t *SimpleAsset) Init(stub shim.ChaincodeStubInterface) peer.Response {
    return shim.Success(nil)
}

// An entry point for the chaincode. Call update, get, or set functions depending on the function name in the chaincode args.
func (t *SimpleAsset) Invoke(stub shim.ChaincodeStubInterface) peer.Response {
    fn, args := stub.GetFunctionAndParameters()

    var result string
    var err error
    if fn == "set" {
	    result, err = set(stub, args)
    } else if fn == "get" {
            result, err = get(stub, args)
    } else {
	    result, err = update(stub, args)
    }
    if err != nil {
            return shim.Error(err.Error())
    }

    return shim.Success([]byte(result))
}

// update stores the new value for the composite key only if the old value for this key from the prestate list is equal to the last value
// for this key from the ledger. Or if the old value for this key from the prestate list is emty %).
// returns error in other cases.
// Args is a string array where elements should be parts of the solid json string which in order should be unmarshallable into UpdateAsset structure
func update(stub shim.ChaincodeStubInterface, args []string) (string, error) {
    data := UpdateAsset{}
    rcargs := strings.Join(args, " ")
    bcargs := []byte(rcargs)
    json.Unmarshal(bcargs, &data)

    if len(data.Commands) == 0 {
	    return "prpr", fmt.Errorf("empty commands")
    }
    index := "index"
    old_states := make(map[string]string)
    for _, element := range data.Prestate {
	    key1 := element[0]
	    key2 := element[1]
	    key3 := element[2]
	    key4 := element[3]
	    value := element[4]
	    comp_key, err := stub.CreateCompositeKey(index, []string{key1, key2, key3, key4})
	    if err != nil {
		    return "", fmt.Errorf("Failed to create composite key: %s", key4)
	    }
	    old_states[comp_key]= value
    }

    var new_states_string string = ""
    var results_string string = ""
    var err error
    var result1 string
    var our_current_value string
    for _, element := range data.Commands {
	    key1 := element[0]
	    key2 := element[1]
	    key3 := element[2]
	    key4 := element[3]
	    new_value := element[4]
	    var comp_key string = ""
	    comp_key, err = stub.CreateCompositeKey(index, []string{key1, key2, key3, key4})
	    if err != nil {
		    return "", fmt.Errorf("Failed to create composite key: %s", key4)
	    }
	    old_value, prs := old_states[comp_key]
	    if prs {
		    our_current_value, err = get(stub, []string{key1,key2,key3,key4})
		    if err != nil {
			    return "prpr", fmt.Errorf("Failed to get to_old_state_saved: %s", comp_key)
		    }
		    if old_value == our_current_value {
			    result1, err = set(stub, element)
			    results_string += result1
			    if err != nil {
				    return "", fmt.Errorf("Failed to set asset: %s", comp_key)
			    }
		    } else {
			    return "INCONSISTENCY!!!", fmt.Errorf("INCONSISTENCY!!!: %s", comp_key)
		    }
	    } else {
		    result1, err = set(stub, element)
		    results_string += result1
		    if err != nil {
			    return "", fmt.Errorf("Failed to set asset: %s", comp_key)
		    }
	    }
	    new_states_string += new_value
    }
    return new_states_string, nil
}

// Set stores the given pair of the composite key and the value on the ledger. If the key exists,
// it will override the value with the new one
// Args is a string array where the first four elements are the parts of the composite key and the fifth one the value
func set(stub shim.ChaincodeStubInterface, args []string) (string, error) {
    if len(args) != 5 {
            return "", fmt.Errorf("Incorrect arguments. Expecting a key and a value")
    }

    key1 := args[0]
    key2 := args[1]
    key3 := args[2]
    key4 := args[3]
    index := "index"
    comp_key, err := stub.CreateCompositeKey(index, []string{key1, key2, key3, key4})
    if err != nil {
	    return "", fmt.Errorf("Failed to create composite key: %s", key4)
    }
    err = stub.PutState(comp_key, []byte(args[4]))
    if err != nil {
            return "", fmt.Errorf("Failed to set asset: %s", comp_key)
    }
    return args[4], nil
}

// Get returns the value of the specified composite key
// Args is a string array where the first four elements are the parts of the composite key and the fifth one the value
func get(stub shim.ChaincodeStubInterface, args []string) (string, error) {
    key1 := args[0]
    key2 := args[1]
    key3 := args[2]
    key4 := args[3]
    index := "index"
    comp_key, err := stub.CreateCompositeKey(index, []string{key1, key2, key3, key4})
    value, err := stub.GetState(comp_key)
    if err != nil {
            return "", fmt.Errorf("Failed to get asset: %s with error: %s", comp_key, err)
    }
    if value == nil {
            return "", fmt.Errorf("Asset not found: %s", comp_key)
    }
    return string(value), nil
}

// main function starts up the chaincode in the container during instantiate
func main() {
    if err := shim.Start(new(SimpleAsset)); err != nil {
            fmt.Printf("Error starting SimpleAsset chaincode: %s", err)
    }
}
