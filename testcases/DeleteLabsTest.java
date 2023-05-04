import java.io.IOException;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.chrome.ChromeOptions;
import org.openqa.selenium.chrome.ChromeDriver;
import org.testng.annotations.Test;
import org.openqa.selenium.By;

public class DeleteLabsTest {

        public static void main(String[] args) throws IOException, InterruptedException {
                System.setProperty("webdriver.chrome.driver", "/usr/bin/chromedriver");
                ChromeOptions chromeOptions = new ChromeOptions();
                // chromeOptions.addArguments("--headless");
                chromeOptions.addArguments("--no-sandbox");
                chromeOptions.addArguments("--ignore-ssl-errors=yes");
                chromeOptions.addArguments("--ignore-certificate-errors");
                WebDriver driver = new ChromeDriver(chromeOptions);

                driver.get("https://dcim2023.com/login/?next=/");
                Thread.sleep(1000);

                driver.findElement(By.xpath("//input[@name='username']")).sendKeys("admin");
                driver.findElement(By.xpath("//input[@name='password']")).sendKeys("admin@123");
                driver.findElement(By.xpath("//button[@type='submit']")).submit();
                Thread.sleep(2000);

                driver.findElements(By.xpath("//a[@href='/dcim/labs/']")).get(1).click();
                Thread.sleep(3000);

                driver.findElement(By.xpath("//a[@href='/dcim/labs/15/']")).click();
                Thread.sleep(3000);

                driver.findElement(By.xpath("//a[@href='#']")).click();
                Thread.sleep(3000);

                driver.findElements(By.xpath("//button[@type='submit']")).get(2).submit();
                Thread.sleep(3000);

                System.out.println("Successfully Deleted Lab !!!");
                driver.quit();
        }
}