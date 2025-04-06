package controller;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class APIControllers {
    @GetMapping("/predictor")
    public String predictor(){
        System.out.println("Predictor");
        return "hello";
    }
}
