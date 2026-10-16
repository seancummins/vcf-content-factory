package com.vcfcf.adapters.rdmtopologypoc;

import java.nio.charset.StandardCharsets;

/** Offline bridge to the actual adapter parser. Input is never echoed or saved. */
public final class RdmFixtureValidate {
    public static void main(String[] args) {
        try {
            RuntimeFixture.parse(new String(System.in.readAllBytes(), StandardCharsets.UTF_8));
            System.out.println("VALID");
        } catch (Throwable failure) {
            System.err.println("Invalid runtime fixture");
            System.exit(2);
        }
    }
}
